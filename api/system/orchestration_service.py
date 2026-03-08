"""Orchestration flow and run-state services for AI-Enterprise."""
from __future__ import annotations

import json
import uuid
from typing import Any, Dict, List, Optional

from fastapi import HTTPException

from api.system.specialist_service import get_specialist

VALID_FLOW_STATUS = {"active", "paused", "archived"}
VALID_FLOW_EXECUTION_MODE = {"locked_pipeline"}
VALID_RUN_STATUS = {"queued", "in_progress", "completed", "failed", "blocked", "cancelled"}
VALID_SCHEDULE_KIND = {"placeholder", "manual", "cron"}


def _normalize_status(value: Optional[str], allowed: set[str], fallback: str, field: str) -> str:
    normalized = str(value or fallback).strip().lower()
    if normalized not in allowed:
        raise HTTPException(status_code=422, detail=f"Invalid {field}")
    return normalized


def _require_known_owner_agent(db_client, agent_id: str) -> str:
    normalized = str(agent_id or "").strip()
    if not normalized:
        raise HTTPException(status_code=422, detail="owner_agent_id is required")
    if normalized in {"father", "engineer"}:
        return normalized
    master = db_client.fetch_one("SELECT id FROM master_agents WHERE id = ?", (normalized,))
    if master:
        return normalized
    specialist = db_client.fetch_one("SELECT id FROM specialist_agents WHERE id = ?", (normalized,))
    if specialist:
        return normalized
    raise HTTPException(status_code=404, detail=f"Unknown owner agent: {normalized}")


def _require_specialist_agent(db_client, agent_id: str) -> Dict[str, Any]:
    normalized = str(agent_id or "").strip()
    if not normalized:
        raise HTTPException(status_code=422, detail="step agent_id is required")
    specialist = get_specialist(db_client=db_client, specialist_id=normalized)
    if specialist is None or str(specialist.get("status") or "").strip().lower() != "active":
        raise HTTPException(status_code=422, detail=f"Flow step agent must be an active specialist: {normalized}")
    return specialist


def _json_value_or_default(value: Any, default: Any, field_name: str) -> Any:
    if value is None:
        return default
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return default
        try:
            parsed = json.loads(raw)
        except Exception as exc:
            raise HTTPException(status_code=422, detail=f"Invalid JSON payload for {field_name}: {exc}") from exc
        if isinstance(parsed, (dict, list)):
            return parsed
    raise HTTPException(status_code=422, detail=f"Invalid JSON payload for {field_name}")


def _parse_json(raw: Any, default: Any) -> Any:
    if raw is None:
        return default
    if isinstance(raw, (dict, list)):
        return raw
    text = str(raw).strip()
    if not text:
        return default
    try:
        parsed = json.loads(text)
    except Exception:
        return default
    if isinstance(parsed, (dict, list)):
        return parsed
    return default


def _safe_objective(template: str, run_context: Dict[str, Any], step: Dict[str, Any]) -> str:
    flat: Dict[str, str] = {}
    for key, value in dict(run_context or {}).items():
        if isinstance(value, (str, int, float, bool)):
            flat[str(key)] = str(value)
        else:
            flat[str(key)] = json.dumps(value, ensure_ascii=True)
    flat["step_order"] = str(step.get("step_order") or "")
    flat["step_agent_id"] = str(step.get("agent_id") or "")

    class _SafeDict(dict):
        def __missing__(self, key):
            return "{" + str(key) + "}"

    safe_template = str(template or "").strip() or "Execute locked flow step"
    try:
        return safe_template.format_map(_SafeDict(flat))
    except Exception:
        return safe_template


def _flow_row(db_client, flow_id: str) -> Dict[str, Any]:
    row = db_client.fetch_one("SELECT * FROM orchestration_flows WHERE id = ?", (flow_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Flow not found")
    return row


def _flow_step_rows(db_client, flow_id: str) -> List[Dict[str, Any]]:
    rows = db_client.fetch_all(
        "SELECT * FROM orchestration_flow_steps WHERE flow_id = ? ORDER BY step_order ASC, created_at ASC",
        (flow_id,),
    )
    for row in rows:
        row["input_contract_json"] = _parse_json(row.get("input_contract_json"), {})
        row["output_schema_json"] = _parse_json(row.get("output_schema_json"), {})
        row["retry_policy_json"] = _parse_json(row.get("retry_policy_json"), {})
    return rows


def list_flows(
    db_client,
    owner_agent_id: Optional[str] = None,
    program_id: Optional[str] = None,
    status: Optional[str] = None,
) -> List[Dict[str, Any]]:
    clauses: List[str] = []
    params: List[Any] = []
    if owner_agent_id:
        clauses.append("owner_agent_id = ?")
        params.append(str(owner_agent_id).strip())
    if program_id:
        clauses.append("program_id = ?")
        params.append(str(program_id).strip())
    if status:
        clauses.append("status = ?")
        params.append(_normalize_status(status, VALID_FLOW_STATUS, "active", "status"))
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    return db_client.fetch_all(
        "SELECT * FROM orchestration_flows "
        f"{where} "
        "ORDER BY updated_at DESC, created_at DESC",
        tuple(params),
    )


def list_flow_runs(
    db_client,
    *,
    status: Optional[str] = None,
    owner_agent_id: Optional[str] = None,
    program_id: Optional[str] = None,
    limit: int = 200,
) -> List[Dict[str, Any]]:
    safe_limit = max(1, min(int(limit), 500))
    clauses: List[str] = []
    params: List[Any] = []
    if status:
        clauses.append("r.status = ?")
        params.append(_normalize_status(status, VALID_RUN_STATUS, "queued", "status"))
    if owner_agent_id:
        clauses.append("f.owner_agent_id = ?")
        params.append(str(owner_agent_id).strip())
    if program_id:
        clauses.append("f.program_id = ?")
        params.append(str(program_id).strip())
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    rows = db_client.fetch_all(
        "SELECT "
        "r.id, r.flow_id, r.trigger_type, r.triggered_by, r.status, r.root_thread_id, r.root_task_id, "
        "r.run_context_json, r.started_at, r.completed_at, r.created_at, "
        "f.name AS flow_name, f.owner_agent_id, f.program_id, "
        "COUNT(rs.id) AS step_count, "
        "SUM(CASE WHEN rs.status = 'queued' THEN 1 ELSE 0 END) AS queued_steps, "
        "SUM(CASE WHEN rs.status = 'in_progress' THEN 1 ELSE 0 END) AS in_progress_steps, "
        "SUM(CASE WHEN rs.status = 'completed' THEN 1 ELSE 0 END) AS completed_steps, "
        "SUM(CASE WHEN rs.status = 'failed' THEN 1 ELSE 0 END) AS failed_steps, "
        "SUM(CASE WHEN rs.status = 'blocked' THEN 1 ELSE 0 END) AS blocked_steps "
        "FROM orchestration_flow_runs r "
        "JOIN orchestration_flows f ON f.id = r.flow_id "
        "LEFT JOIN orchestration_flow_run_steps rs ON rs.run_id = r.id "
        f"{where} "
        "GROUP BY r.id "
        "ORDER BY COALESCE(r.completed_at, r.started_at, r.created_at) DESC "
        "LIMIT ?",
        tuple(params + [safe_limit]),
    )
    for row in rows:
        row["run_context_json"] = _parse_json(row.get("run_context_json"), {})
        row["step_counts"] = {
            "total": int(row.get("step_count") or 0),
            "queued": int(row.get("queued_steps") or 0),
            "in_progress": int(row.get("in_progress_steps") or 0),
            "completed": int(row.get("completed_steps") or 0),
            "failed": int(row.get("failed_steps") or 0),
            "blocked": int(row.get("blocked_steps") or 0),
        }
    return rows


def get_flow(db_client, flow_id: str) -> Dict[str, Any]:
    row = _flow_row(db_client=db_client, flow_id=flow_id)
    row["steps"] = _flow_step_rows(db_client=db_client, flow_id=flow_id)
    return row


def create_flow(
    db_client,
    owner_agent_id: str,
    name: str,
    program_id: Optional[str] = None,
    description: str = "",
    execution_mode: str = "locked_pipeline",
    schedule_kind: str = "placeholder",
    schedule_expr: str = "",
    status: str = "active",
    created_by: str = "system",
) -> Dict[str, Any]:
    owner = _require_known_owner_agent(db_client=db_client, agent_id=owner_agent_id)
    safe_name = str(name or "").strip()
    if not safe_name:
        raise HTTPException(status_code=422, detail="Flow name is required")
    mode = _normalize_status(execution_mode, VALID_FLOW_EXECUTION_MODE, "locked_pipeline", "execution_mode")
    normalized_status = _normalize_status(status, VALID_FLOW_STATUS, "active", "status")
    normalized_schedule_kind = _normalize_status(schedule_kind, VALID_SCHEDULE_KIND, "placeholder", "schedule_kind")

    flow_id = str(uuid.uuid4())
    db_client.execute(
        "INSERT INTO orchestration_flows "
        "(id, owner_agent_id, program_id, name, description, execution_mode, schedule_kind, schedule_expr, status, created_by, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))",
        (
            flow_id,
            owner,
            str(program_id or "").strip() or None,
            safe_name,
            str(description or "").strip(),
            mode,
            normalized_schedule_kind,
            str(schedule_expr or "").strip(),
            normalized_status,
            str(created_by or "system").strip() or "system",
        ),
    )
    return get_flow(db_client=db_client, flow_id=flow_id)


def update_flow(
    db_client,
    flow_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    execution_mode: Optional[str] = None,
    schedule_kind: Optional[str] = None,
    schedule_expr: Optional[str] = None,
    status: Optional[str] = None,
    owner_agent_id: Optional[str] = None,
    program_id: Optional[str] = None,
) -> Dict[str, Any]:
    current = _flow_row(db_client=db_client, flow_id=flow_id)
    next_owner = _require_known_owner_agent(db_client=db_client, agent_id=owner_agent_id or current["owner_agent_id"])
    next_name = str(name if name is not None else current["name"]).strip()
    if not next_name:
        raise HTTPException(status_code=422, detail="Flow name is required")
    next_description = str(description if description is not None else current.get("description") or "").strip()
    next_mode = _normalize_status(
        execution_mode if execution_mode is not None else current.get("execution_mode"),
        VALID_FLOW_EXECUTION_MODE,
        "locked_pipeline",
        "execution_mode",
    )
    next_schedule_kind = _normalize_status(
        schedule_kind if schedule_kind is not None else current.get("schedule_kind"),
        VALID_SCHEDULE_KIND,
        "placeholder",
        "schedule_kind",
    )
    next_schedule_expr = str(schedule_expr if schedule_expr is not None else current.get("schedule_expr") or "").strip()
    next_status = _normalize_status(status if status is not None else current.get("status"), VALID_FLOW_STATUS, "active", "status")
    next_program = str(program_id if program_id is not None else current.get("program_id") or "").strip() or None

    db_client.execute(
        "UPDATE orchestration_flows SET owner_agent_id = ?, program_id = ?, name = ?, description = ?, "
        "execution_mode = ?, schedule_kind = ?, schedule_expr = ?, status = ?, updated_at = datetime('now') WHERE id = ?",
        (
            next_owner,
            next_program,
            next_name,
            next_description,
            next_mode,
            next_schedule_kind,
            next_schedule_expr,
            next_status,
            flow_id,
        ),
    )
    return get_flow(db_client=db_client, flow_id=flow_id)


def list_flow_steps(db_client, flow_id: str) -> List[Dict[str, Any]]:
    _ = _flow_row(db_client=db_client, flow_id=flow_id)
    return _flow_step_rows(db_client=db_client, flow_id=flow_id)


def create_flow_step(
    db_client,
    flow_id: str,
    step_order: int,
    agent_id: str,
    objective_template: str,
    input_contract_json: Any = None,
    output_schema_json: Any = None,
    retry_policy_json: Any = None,
    on_failure: str = "escalate",
    timeout_seconds: int = 120,
) -> Dict[str, Any]:
    _ = _flow_row(db_client=db_client, flow_id=flow_id)
    _ = _require_specialist_agent(db_client=db_client, agent_id=agent_id)
    safe_order = int(step_order)
    if safe_order <= 0:
        raise HTTPException(status_code=422, detail="step_order must be greater than zero")
    safe_objective = str(objective_template or "").strip()
    if not safe_objective:
        raise HTTPException(status_code=422, detail="objective_template is required")

    step_id = str(uuid.uuid4())
    db_client.execute(
        "INSERT INTO orchestration_flow_steps "
        "(id, flow_id, step_order, agent_id, objective_template, input_contract_json, output_schema_json, retry_policy_json, on_failure, timeout_seconds, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))",
        (
            step_id,
            flow_id,
            safe_order,
            str(agent_id).strip(),
            safe_objective,
            json.dumps(_json_value_or_default(input_contract_json, {}, "input_contract_json")),
            json.dumps(_json_value_or_default(output_schema_json, {}, "output_schema_json")),
            json.dumps(_json_value_or_default(retry_policy_json, {}, "retry_policy_json")),
            str(on_failure or "escalate").strip() or "escalate",
            max(1, int(timeout_seconds or 120)),
        ),
    )
    steps = _flow_step_rows(db_client=db_client, flow_id=flow_id)
    return next(item for item in steps if item["id"] == step_id)


def update_flow_step(
    db_client,
    flow_id: str,
    step_id: str,
    step_order: Optional[int] = None,
    agent_id: Optional[str] = None,
    objective_template: Optional[str] = None,
    input_contract_json: Any = None,
    output_schema_json: Any = None,
    retry_policy_json: Any = None,
    on_failure: Optional[str] = None,
    timeout_seconds: Optional[int] = None,
) -> Dict[str, Any]:
    _ = _flow_row(db_client=db_client, flow_id=flow_id)
    current = db_client.fetch_one(
        "SELECT * FROM orchestration_flow_steps WHERE id = ? AND flow_id = ?",
        (step_id, flow_id),
    )
    if not current:
        raise HTTPException(status_code=404, detail="Flow step not found")

    next_order = int(step_order if step_order is not None else current["step_order"])
    if next_order <= 0:
        raise HTTPException(status_code=422, detail="step_order must be greater than zero")
    next_agent = str(agent_id if agent_id is not None else current["agent_id"]).strip()
    _ = _require_specialist_agent(db_client=db_client, agent_id=next_agent)
    next_objective = str(objective_template if objective_template is not None else current["objective_template"]).strip()
    if not next_objective:
        raise HTTPException(status_code=422, detail="objective_template is required")

    current_input = _parse_json(current.get("input_contract_json"), {})
    current_output = _parse_json(current.get("output_schema_json"), {})
    current_retry = _parse_json(current.get("retry_policy_json"), {})

    next_input = _json_value_or_default(input_contract_json, current_input, "input_contract_json")
    next_output = _json_value_or_default(output_schema_json, current_output, "output_schema_json")
    next_retry = _json_value_or_default(retry_policy_json, current_retry, "retry_policy_json")
    next_on_failure = str(on_failure if on_failure is not None else current.get("on_failure") or "escalate").strip() or "escalate"
    next_timeout = max(1, int(timeout_seconds if timeout_seconds is not None else current.get("timeout_seconds") or 120))

    db_client.execute(
        "UPDATE orchestration_flow_steps SET step_order = ?, agent_id = ?, objective_template = ?, "
        "input_contract_json = ?, output_schema_json = ?, retry_policy_json = ?, on_failure = ?, timeout_seconds = ?, "
        "updated_at = datetime('now') WHERE id = ? AND flow_id = ?",
        (
            next_order,
            next_agent,
            next_objective,
            json.dumps(next_input),
            json.dumps(next_output),
            json.dumps(next_retry),
            next_on_failure,
            next_timeout,
            step_id,
            flow_id,
        ),
    )
    steps = _flow_step_rows(db_client=db_client, flow_id=flow_id)
    return next(item for item in steps if item["id"] == step_id)


def get_flow_run(db_client, run_id: str) -> Dict[str, Any]:
    run = db_client.fetch_one("SELECT * FROM orchestration_flow_runs WHERE id = ?", (run_id,))
    if not run:
        raise HTTPException(status_code=404, detail="Flow run not found")
    flow = _flow_row(db_client=db_client, flow_id=run["flow_id"])
    run_context = _parse_json(run.get("run_context_json"), {})

    step_rows = db_client.fetch_all(
        "SELECT rs.*, s.step_order, s.agent_id, s.objective_template, s.input_contract_json, s.output_schema_json, "
        "s.retry_policy_json, s.on_failure, s.timeout_seconds, "
        "t.status AS task_status, t.execution_stage AS task_execution_stage, t.objective AS task_objective, "
        "t.specialist_id AS task_specialist_id, t.started_at AS task_started_at, t.completed_at AS task_completed_at "
        "FROM orchestration_flow_run_steps rs "
        "JOIN orchestration_flow_steps s ON s.id = rs.step_id "
        "LEFT JOIN task_queue t ON t.id = rs.task_id "
        "WHERE rs.run_id = ? "
        "ORDER BY s.step_order ASC",
        (run_id,),
    )
    steps: List[Dict[str, Any]] = []
    for row in step_rows:
        item = dict(row)
        item["input_contract_json"] = _parse_json(item.get("input_contract_json"), {})
        item["output_schema_json"] = _parse_json(item.get("output_schema_json"), {})
        item["retry_policy_json"] = _parse_json(item.get("retry_policy_json"), {})
        steps.append(item)

    status_counts: Dict[str, int] = {}
    for item in steps:
        key = str(item.get("status") or "queued")
        status_counts[key] = int(status_counts.get(key, 0)) + 1

    return {
        "run": {**run, "run_context_json": run_context},
        "flow": flow,
        "steps": steps,
        "status_counts": status_counts,
    }


def run_flow(
    db_client,
    flow_id: str,
    trigger_type: str = "manual",
    triggered_by: str = "workspace",
    root_thread_id: Optional[str] = None,
    run_context_json: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    flow = _flow_row(db_client=db_client, flow_id=flow_id)
    if str(flow.get("status") or "").strip().lower() != "active":
        raise HTTPException(status_code=409, detail="Flow is not active")
    if str(flow.get("execution_mode") or "").strip().lower() != "locked_pipeline":
        raise HTTPException(status_code=409, detail="Flow must use locked_pipeline execution mode")

    steps = _flow_step_rows(db_client=db_client, flow_id=flow_id)
    if not steps:
        raise HTTPException(status_code=422, detail="Flow has no steps")

    for step in steps:
        _ = _require_specialist_agent(db_client=db_client, agent_id=str(step["agent_id"]))

    run_id = str(uuid.uuid4())
    run_context = dict(run_context_json or {})
    if root_thread_id:
        thread = db_client.fetch_one("SELECT id FROM chat_threads WHERE id = ?", (root_thread_id,))
        if not thread:
            raise HTTPException(status_code=404, detail="Root thread not found")

    db_client.execute(
        "INSERT INTO orchestration_flow_runs "
        "(id, flow_id, trigger_type, triggered_by, status, root_thread_id, root_task_id, run_context_json, started_at, completed_at, created_at) "
        "VALUES (?, ?, ?, ?, 'queued', ?, NULL, ?, NULL, NULL, datetime('now'))",
        (
            run_id,
            flow_id,
            str(trigger_type or "manual").strip() or "manual",
            str(triggered_by or "workspace").strip() or "workspace",
            str(root_thread_id or "").strip() or None,
            json.dumps(run_context),
        ),
    )

    first_task_id: Optional[str] = None
    previous_task_id: Optional[str] = None
    priority = str(run_context.get("priority") or "P2").strip().upper()
    if priority not in {"P0", "P1", "P2", "P3"}:
        priority = "P2"
    resolved_program_id = str(run_context.get("program_id") or flow.get("program_id") or "").strip() or None
    resolved_application_id = str(run_context.get("application_id") or "").strip() or None

    for index, step in enumerate(steps):
        task_id = str(uuid.uuid4())
        if first_task_id is None:
            first_task_id = task_id
        objective = _safe_objective(
            template=str(step.get("objective_template") or ""),
            run_context=run_context,
            step=step,
        )
        display_name = f"{flow.get('name') or flow_id} · step {step.get('step_order')}"
        task_status = "in_progress" if index == 0 else "pending"
        task_stage = "in_progress" if index == 0 else "delegated"
        start_marker = "now" if index == 0 else ""
        task_context = {
            "flow_run": {
                "run_id": run_id,
                "flow_id": flow_id,
                "step_id": step["id"],
                "step_order": step.get("step_order"),
            },
            "input_contract": step.get("input_contract_json") or {},
            "run_context": run_context,
            "execution_mode": "locked_pipeline",
        }
        db_client.execute(
            "INSERT INTO task_queue "
            "(id, master_id, specialist_id, orchestrator_master_id, objective, display_name, context, priority, status, execution_stage, "
            "parent_task_id, program_id, application_id, correlation_id, delegation_schema_version, assigned_at, started_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), "
            "CASE WHEN ? = 'now' THEN datetime('now') ELSE NULL END)",
            (
                task_id,
                str(flow["owner_agent_id"]),
                str(step["agent_id"]),
                str(flow["owner_agent_id"]),
                objective,
                display_name,
                json.dumps(task_context),
                priority,
                task_status,
                task_stage,
                previous_task_id,
                resolved_program_id,
                resolved_application_id,
                run_id,
                "flow_locked_v2",
                start_marker,
            ),
        )
        db_client.execute(
            "INSERT INTO orchestration_flow_run_steps "
            "(id, run_id, step_id, task_id, status, output_valid, result_packet_id, escalation_id, started_at, completed_at, created_at) "
            "VALUES (?, ?, ?, ?, ?, 0, NULL, NULL, "
            "CASE WHEN ? = 'now' THEN datetime('now') ELSE NULL END, NULL, datetime('now'))",
            (
                str(uuid.uuid4()),
                run_id,
                step["id"],
                task_id,
                "in_progress" if index == 0 else "queued",
                start_marker,
            ),
        )
        db_client.execute(
            "INSERT INTO task_flow_locks (task_id, run_id, step_id, locked_agent_id, output_schema_json, created_at) "
            "VALUES (?, ?, ?, ?, ?, datetime('now'))",
            (
                task_id,
                run_id,
                step["id"],
                str(step["agent_id"]),
                json.dumps(step.get("output_schema_json") or {}),
            ),
        )
        previous_task_id = task_id

    db_client.execute(
        "UPDATE orchestration_flow_runs SET status = 'in_progress', root_task_id = ?, started_at = datetime('now') WHERE id = ?",
        (first_task_id, run_id),
    )
    return get_flow_run(db_client=db_client, run_id=run_id)


def update_run_context(
    db_client,
    run_id: str,
    run_context_json: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    safe_run_id = str(run_id or "").strip()
    run = db_client.fetch_one("SELECT id FROM orchestration_flow_runs WHERE id = ?", (safe_run_id,))
    if not run:
        raise HTTPException(status_code=404, detail="Flow run not found")
    payload = _json_value_or_default(run_context_json, {}, "run_context_json")
    db_client.execute(
        "UPDATE orchestration_flow_runs SET run_context_json = ? WHERE id = ?",
        (json.dumps(payload), safe_run_id),
    )
    updated = get_flow_run(db_client=db_client, run_id=safe_run_id)
    updated["updated_context_json"] = payload
    return updated


def retrigger_run_step(
    db_client,
    run_id: str,
    step_id: str,
    triggered_by: str = "workspace",
) -> Dict[str, Any]:
    safe_run_id = str(run_id or "").strip()
    safe_step_id = str(step_id or "").strip()
    if not safe_run_id or not safe_step_id:
        raise HTTPException(status_code=422, detail="run_id and step_id are required")

    run = db_client.fetch_one(
        "SELECT r.*, f.name AS flow_name, f.owner_agent_id, f.program_id "
        "FROM orchestration_flow_runs r "
        "JOIN orchestration_flows f ON f.id = r.flow_id "
        "WHERE r.id = ?",
        (safe_run_id,),
    )
    if not run:
        raise HTTPException(status_code=404, detail="Flow run not found")

    step_row = db_client.fetch_one(
        "SELECT rs.*, s.step_order, s.agent_id, s.objective_template, s.input_contract_json, s.output_schema_json "
        "FROM orchestration_flow_run_steps rs "
        "JOIN orchestration_flow_steps s ON s.id = rs.step_id "
        "WHERE rs.run_id = ? AND rs.step_id = ?",
        (safe_run_id, safe_step_id),
    )
    if not step_row:
        raise HTTPException(status_code=404, detail="Flow run step not found")

    step_status = str(step_row.get("status") or "").strip().lower()
    if step_status not in {"failed", "blocked"}:
        raise HTTPException(status_code=409, detail="Only failed or blocked steps can be retriggered")

    downstream = db_client.fetch_one(
        "SELECT COUNT(*) AS total FROM orchestration_flow_run_steps rs "
        "JOIN orchestration_flow_steps s ON s.id = rs.step_id "
        "WHERE rs.run_id = ? AND s.step_order > ? AND rs.status = 'completed'",
        (safe_run_id, int(step_row.get("step_order") or 0)),
    )
    if int((downstream or {}).get("total") or 0) > 0:
        raise HTTPException(
            status_code=409,
            detail="Cannot retrigger step because downstream steps are already completed.",
        )

    old_task_id = str(step_row.get("task_id") or "").strip()
    existing_task = db_client.fetch_one("SELECT * FROM task_queue WHERE id = ?", (old_task_id,)) if old_task_id else None
    run_context = _parse_json(run.get("run_context_json"), {})
    input_contract = _parse_json(step_row.get("input_contract_json"), {})
    output_schema = _parse_json(step_row.get("output_schema_json"), {})

    new_task_id = str(uuid.uuid4())
    objective = _safe_objective(
        template=str(step_row.get("objective_template") or ""),
        run_context=run_context,
        step=step_row,
    )
    display_name = f"{run.get('flow_name') or run.get('flow_id')} · step {step_row.get('step_order')} retry"
    priority = str((existing_task or {}).get("priority") or run_context.get("priority") or "P2").strip().upper()
    if priority not in {"P0", "P1", "P2", "P3"}:
        priority = "P2"
    program_id = str((existing_task or {}).get("program_id") or run.get("program_id") or run_context.get("program_id") or "").strip() or None
    application_id = str((existing_task or {}).get("application_id") or run_context.get("application_id") or "").strip() or None
    task_context = {
        "flow_run": {
            "run_id": safe_run_id,
            "flow_id": run.get("flow_id"),
            "step_id": safe_step_id,
            "step_order": step_row.get("step_order"),
            "retriggered_by": str(triggered_by or "workspace"),
            "retriggered_from_task_id": old_task_id or None,
        },
        "input_contract": input_contract,
        "run_context": run_context,
        "execution_mode": "locked_pipeline",
    }
    db_client.execute(
        "INSERT INTO task_queue "
        "(id, master_id, specialist_id, orchestrator_master_id, objective, display_name, context, priority, status, execution_stage, "
        "parent_task_id, program_id, application_id, correlation_id, delegation_schema_version, assigned_at, started_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'in_progress', 'delegated', ?, ?, ?, ?, 'flow_locked_v2', datetime('now'), datetime('now'))",
        (
            new_task_id,
            str(run.get("owner_agent_id") or ""),
            str(step_row.get("agent_id") or ""),
            str(run.get("owner_agent_id") or ""),
            objective,
            display_name,
            json.dumps(task_context),
            priority,
            old_task_id or None,
            program_id,
            application_id,
            safe_run_id,
        ),
    )
    db_client.execute(
        "UPDATE orchestration_flow_run_steps SET task_id = ?, status = 'in_progress', output_valid = 0, "
        "result_packet_id = NULL, escalation_id = NULL, started_at = datetime('now'), completed_at = NULL "
        "WHERE run_id = ? AND step_id = ?",
        (new_task_id, safe_run_id, safe_step_id),
    )
    db_client.execute(
        "INSERT INTO task_flow_locks (task_id, run_id, step_id, locked_agent_id, output_schema_json, created_at) "
        "VALUES (?, ?, ?, ?, ?, datetime('now'))",
        (
            new_task_id,
            safe_run_id,
            safe_step_id,
            str(step_row.get("agent_id") or ""),
            json.dumps(output_schema),
        ),
    )
    db_client.execute(
        "UPDATE orchestration_flow_runs SET status = 'in_progress', completed_at = NULL, started_at = COALESCE(started_at, datetime('now')) "
        "WHERE id = ?",
        (safe_run_id,),
    )
    payload = get_flow_run(db_client=db_client, run_id=safe_run_id)
    payload["retriggered_step"] = {
        "step_id": safe_step_id,
        "new_task_id": new_task_id,
        "previous_task_id": old_task_id or None,
        "triggered_by": str(triggered_by or "workspace"),
    }
    return payload


def hub_overview(db_client) -> Dict[str, Any]:
    active_threads = db_client.fetch_all(
        "SELECT id, agent_id, title, status, execution_mode, default_model_profile_id, override_model_profile_id, "
        "program_id, created_at, updated_at, last_message_at "
        "FROM chat_threads WHERE status = 'active' "
        "ORDER BY COALESCE(last_message_at, updated_at, created_at) DESC LIMIT 200"
    )
    sessions: List[Dict[str, Any]] = []
    for thread in active_threads:
        rows = db_client.fetch_all(
            "SELECT role, meta_json FROM chat_messages WHERE thread_id = ? ORDER BY created_at ASC",
            (thread["id"],),
        )
        estimated_cost = 0.0
        for row in rows:
            if str(row.get("role") or "") != "assistant":
                continue
            meta = _parse_json(row.get("meta_json"), {})
            turn_cost = meta.get("estimated_turn_cost_usd")
            if isinstance(turn_cost, dict):
                estimated_cost += float(turn_cost.get("total") or 0.0)
        sessions.append(
            {
                "thread_id": thread["id"],
                "agent_id": thread["agent_id"],
                "title": thread["title"],
                "execution_mode": thread.get("execution_mode") or "free_reasoning",
                "model_profile_id": thread.get("override_model_profile_id") or thread.get("default_model_profile_id"),
                "program_id": thread.get("program_id"),
                "message_count": len(rows),
                "estimated_session_cost_usd": round(estimated_cost, 6),
                "last_activity_at": thread.get("last_message_at") or thread.get("updated_at") or thread.get("created_at"),
            }
        )

    flows = db_client.fetch_all(
        "SELECT id, owner_agent_id, program_id, name, description, execution_mode, schedule_kind, schedule_expr, status, created_by, created_at, updated_at "
        "FROM orchestration_flows ORDER BY updated_at DESC LIMIT 100"
    )
    run_counts_rows = db_client.fetch_all("SELECT status, COUNT(*) AS total FROM orchestration_flow_runs GROUP BY status")
    run_counts = {str(item["status"]): int(item["total"]) for item in run_counts_rows}
    open_escalations = db_client.fetch_one("SELECT COUNT(*) AS total FROM task_escalations WHERE status = 'open'")
    open_errors = db_client.fetch_one("SELECT COUNT(*) AS total FROM error_log WHERE status = 'open'")

    return {
        "sessions": sessions,
        "flows": flows,
        "counts": {
            "active_sessions": len(sessions),
            "total_flows": len(flows),
            "active_flows": sum(1 for item in flows if str(item.get("status") or "") == "active"),
            "in_progress_runs": int(run_counts.get("in_progress", 0)),
            "queued_runs": int(run_counts.get("queued", 0)),
            "blocked_runs": int(run_counts.get("blocked", 0)),
        },
        "health": {
            "open_escalations": int((open_escalations or {}).get("total") or 0),
            "open_errors": int((open_errors or {}).get("total") or 0),
        },
    }


def hub_activity(db_client, limit: int = 200) -> Dict[str, Any]:
    safe_limit = max(1, min(int(limit), 500))
    events: List[Dict[str, Any]] = []

    task_rows = db_client.fetch_all(
        "SELECT id, master_id, specialist_id, status, execution_stage, objective, updated_at "
        "FROM task_queue ORDER BY updated_at DESC LIMIT ?",
        (safe_limit,),
    )
    for row in task_rows:
        events.append(
            {
                "kind": "task",
                "id": row["id"],
                "timestamp": row.get("updated_at"),
                "summary": f"Task {row['id']} is {row.get('status')} ({row.get('execution_stage')})",
                "payload": row,
            }
        )

    escalation_rows = db_client.fetch_all(
        "SELECT id, task_id, specialist_id, blocker_type, severity, status, created_at "
        "FROM task_escalations ORDER BY created_at DESC LIMIT ?",
        (safe_limit,),
    )
    for row in escalation_rows:
        events.append(
            {
                "kind": "escalation",
                "id": row["id"],
                "timestamp": row.get("created_at"),
                "summary": f"Escalation {row['id']} ({row.get('severity')}) for task {row.get('task_id')}",
                "payload": row,
            }
        )

    invocation_rows = db_client.fetch_all(
        "SELECT id, specialist_id, tool_key, action, success, task_id, thread_id, created_at "
        "FROM specialist_invocations ORDER BY created_at DESC LIMIT ?",
        (safe_limit,),
    )
    for row in invocation_rows:
        events.append(
            {
                "kind": "invocation",
                "id": row["id"],
                "timestamp": row.get("created_at"),
                "summary": f"Invocation {row.get('tool_key')}:{row.get('action')} by {row.get('specialist_id')}",
                "payload": row,
            }
        )

    run_rows = db_client.fetch_all(
        "SELECT id, flow_id, status, trigger_type, triggered_by, created_at, started_at, completed_at "
        "FROM orchestration_flow_runs ORDER BY created_at DESC LIMIT ?",
        (safe_limit,),
    )
    for row in run_rows:
        events.append(
            {
                "kind": "flow_run",
                "id": row["id"],
                "timestamp": row.get("completed_at") or row.get("started_at") or row.get("created_at"),
                "summary": f"Flow run {row['id']} is {row.get('status')}",
                "payload": row,
            }
        )

    run_step_rows = db_client.fetch_all(
        "SELECT id, run_id, step_id, task_id, status, output_valid, created_at, completed_at "
        "FROM orchestration_flow_run_steps ORDER BY created_at DESC LIMIT ?",
        (safe_limit,),
    )
    for row in run_step_rows:
        events.append(
            {
                "kind": "flow_step",
                "id": row["id"],
                "timestamp": row.get("completed_at") or row.get("created_at"),
                "summary": f"Flow step {row.get('step_id')} is {row.get('status')}",
                "payload": row,
            }
        )

    events.sort(key=lambda item: str(item.get("timestamp") or ""), reverse=True)
    return {"events": events[:safe_limit], "limit": safe_limit}
