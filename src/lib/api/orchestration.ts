import { requestJson } from "./client";

export type RunSummary = {
  id: string;
  flow_id: string;
  flow_name: string;
  owner_agent_id: string;
  program_id?: string | null;
  status: string;
  trigger_type: string;
  triggered_by: string;
  run_context_json: Record<string, unknown>;
  started_at?: string | null;
  completed_at?: string | null;
  created_at: string;
  step_counts: {
    total: number;
    queued: number;
    in_progress: number;
    completed: number;
    failed: number;
    blocked: number;
  };
};

export type OrchestrationOverviewPayload = {
  generated_at: string;
  counts: {
    active_sessions: number;
    total_flows: number;
    active_flows: number;
    in_progress_runs: number;
    queued_runs: number;
    blocked_runs: number;
  };
  health: {
    open_escalations: number;
    open_errors: number;
  };
  flows: Array<{
    id: string;
    owner_agent_id: string;
    program_id?: string | null;
    name: string;
    description: string;
    execution_mode: string;
    schedule_kind: string;
    schedule_expr: string;
    status: string;
    created_by: string;
    created_at: string;
    updated_at: string;
  }>;
  sessions: Array<{
    thread_id: string;
    agent_id: string;
    title: string;
    execution_mode: string;
    model_profile_id?: string | null;
    program_id?: string | null;
    message_count: number;
    estimated_session_cost_usd: number;
    last_activity_at: string | null;
  }>;
  recent_runs: RunSummary[];
};

export type OrchestrationRunsPayload = {
  generated_at: string;
  runs: RunSummary[];
  filters: {
    status?: string | null;
    owner_agent_id?: string | null;
    program_id?: string | null;
    limit: number;
  };
  totals: {
    runs: number;
    in_progress: number;
    blocked: number;
    completed: number;
  };
};

export type RunDetailPayload = {
  generated_at?: string;
  run: {
    id: string;
    flow_id: string;
    trigger_type: string;
    triggered_by: string;
    status: string;
    root_thread_id?: string | null;
    root_task_id?: string | null;
    run_context_json: Record<string, unknown>;
    started_at?: string | null;
    completed_at?: string | null;
    created_at: string;
  };
  flow: {
    id: string;
    owner_agent_id: string;
    program_id?: string | null;
    name: string;
    description: string;
    execution_mode: string;
    schedule_kind: string;
    schedule_expr: string;
    status: string;
    created_by: string;
    created_at: string;
    updated_at: string;
    steps?: unknown[];
  };
  steps: Array<{
    id: string;
    run_id: string;
    step_id: string;
    task_id: string | null;
    status: string;
    output_valid: number;
    started_at?: string | null;
    completed_at?: string | null;
    step_order: number;
    agent_id: string;
    objective_template: string;
    input_contract_json: Record<string, unknown>;
    output_schema_json: Record<string, unknown>;
    retry_policy_json: Record<string, unknown>;
    on_failure: string;
    timeout_seconds: number;
    task_status?: string | null;
    task_execution_stage?: string | null;
  }>;
  status_counts: Record<string, number>;
  updated_context_json?: Record<string, unknown>;
  retriggered_step?: {
    step_id: string;
    new_task_id: string;
    previous_task_id?: string | null;
    triggered_by: string;
  };
};

export function getOrchestrationOverview(headers: Record<string, string>, signal?: AbortSignal) {
  return requestJson<OrchestrationOverviewPayload>("/api/control-ui/orchestration/overview", {
    headers,
    signal,
  });
}

export function getOrchestrationRuns(headers: Record<string, string>, signal?: AbortSignal) {
  return requestJson<OrchestrationRunsPayload>("/api/control-ui/orchestration/runs", {
    headers,
    signal,
  });
}

export function getOrchestrationRun(runId: string, headers: Record<string, string>, signal?: AbortSignal) {
  return requestJson<RunDetailPayload>(`/api/control-ui/orchestration/runs/${encodeURIComponent(runId)}`, {
    headers,
    signal,
  });
}

export function triggerOrchestrationFlow(
  flowId: string,
  headers: Record<string, string>,
  runContextJson: Record<string, unknown> = {},
) {
  return requestJson<RunDetailPayload>("/api/control-ui/orchestration/trigger", {
    method: "POST",
    headers,
    body: {
      flow_id: flowId,
      trigger_type: "manual",
      triggered_by: "workspace-ui",
      run_context_json: runContextJson,
    },
  });
}

export function patchRunContext(
  runId: string,
  runContextJson: Record<string, unknown>,
  headers: Record<string, string>,
) {
  return requestJson<RunDetailPayload>(`/api/orchestration/runs/${encodeURIComponent(runId)}/context`, {
    method: "PATCH",
    headers,
    body: { run_context_json: runContextJson },
  });
}

export function retriggerRunStep(runId: string, stepId: string, headers: Record<string, string>) {
  return requestJson<RunDetailPayload>(
    `/api/orchestration/runs/${encodeURIComponent(runId)}/steps/${encodeURIComponent(stepId)}/retrigger`,
    {
      method: "POST",
      headers,
      body: { triggered_by: "workspace-ui" },
    },
  );
}
