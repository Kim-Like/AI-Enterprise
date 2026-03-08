import { useEffect, useMemo, useState } from "react";
import { ApiError } from "../../lib/api/client";
import {
  getOrchestrationOverview,
  getOrchestrationRun,
  getOrchestrationRuns,
  patchRunContext,
  retriggerRunStep,
  triggerOrchestrationFlow,
  type OrchestrationOverviewPayload,
  type OrchestrationRunsPayload,
  type RunDetailPayload,
} from "../../lib/api/orchestration";
import { useControlSession } from "../../lib/control-session";
import { PageScaffold } from "../shared/PageScaffold";
import { HealthBar } from "../shared/HealthBar";
import { SessionRequired } from "../shared/SessionRequired";
import { StatusDot } from "../shared/StatusDot";

export function OrchestrationCenter() {
  const { hasSession, buildHeaders } = useControlSession();
  const [overview, setOverview] = useState<OrchestrationOverviewPayload | null>(null);
  const [runs, setRuns] = useState<OrchestrationRunsPayload | null>(null);
  const [selectedRun, setSelectedRun] = useState<RunDetailPayload | null>(null);
  const [selectedFlowId, setSelectedFlowId] = useState("");
  const [contextDraft, setContextDraft] = useState("{}");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!hasSession) {
      setOverview(null);
      setRuns(null);
      setSelectedRun(null);
      return;
    }
    let active = true;
    const controller = new AbortController();
    async function load() {
      try {
        const [overviewPayload, runsPayload] = await Promise.all([
          getOrchestrationOverview(buildHeaders(), controller.signal),
          getOrchestrationRuns(buildHeaders(), controller.signal),
        ]);
        if (!active) return;
        setOverview(overviewPayload);
        setRuns(runsPayload);
        setSelectedFlowId((current) => current || overviewPayload.flows[0]?.id || "");
        const runId = runsPayload.runs[0]?.id;
        if (runId) {
          const detail = await getOrchestrationRun(runId, buildHeaders(), controller.signal);
          if (!active) return;
          setSelectedRun(detail);
          setContextDraft(JSON.stringify(detail.run.run_context_json ?? {}, null, 2));
        }
        setError("");
      } catch (err) {
        if (active) {
          setError(err instanceof ApiError ? err.detail : "Unable to load orchestration data");
        }
      }
    }
    void load();
    return () => {
      active = false;
      controller.abort();
    };
  }, [buildHeaders, hasSession]);

  const counts = overview?.counts;
  const maxSteps = useMemo(() => Math.max(1, ...(selectedRun?.steps.map((step) => step.step_order) ?? [1])), [selectedRun]);

  async function selectRun(runId: string) {
    try {
      const payload = await getOrchestrationRun(runId, buildHeaders());
      setSelectedRun(payload);
      setContextDraft(JSON.stringify(payload.run.run_context_json ?? {}, null, 2));
      setError("");
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Unable to load run detail");
    }
  }

  async function triggerFlow() {
    if (!selectedFlowId) return;
    try {
      const payload = await triggerOrchestrationFlow(selectedFlowId, buildHeaders(), {});
      setSelectedRun(payload);
      setContextDraft(JSON.stringify(payload.run.run_context_json ?? {}, null, 2));
      const refreshedRuns = await getOrchestrationRuns(buildHeaders());
      setRuns(refreshedRuns);
      setError("");
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Unable to trigger flow");
    }
  }

  async function saveContext() {
    if (!selectedRun) return;
    try {
      const parsed = JSON.parse(contextDraft) as Record<string, unknown>;
      const payload = await patchRunContext(selectedRun.run.id, parsed, buildHeaders());
      setSelectedRun(payload);
      setContextDraft(JSON.stringify(payload.run.run_context_json ?? {}, null, 2));
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to save context");
    }
  }

  async function retrigger(stepId: string) {
    if (!selectedRun) return;
    try {
      const payload = await retriggerRunStep(selectedRun.run.id, stepId, buildHeaders());
      setSelectedRun(payload);
      const refreshedRuns = await getOrchestrationRuns(buildHeaders());
      setRuns(refreshedRuns);
      setError("");
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Unable to retrigger step");
    }
  }

  return (
    <PageScaffold
      eyebrow="Orchestration"
      title="Run Queue And Timeline"
      description="Live orchestration state from the clean Phase 5 backend, including manual trigger, run detail, and step retrigger support."
      actions={<StatusDot tone={hasSession ? "green" : "red"} label={hasSession ? "Live" : "Session required"} />}
    >
      {!hasSession ? (
        <SessionRequired detail="Open Operator Session to load run state and trigger orchestration flows." />
      ) : null}
      {error ? <div className="error-panel">{error}</div> : null}
      <div className="metric-grid">
        <div className="metric-card">
          <p className="metric-label">Active flows</p>
          <p className="metric-value">{counts?.active_flows ?? "-"}</p>
        </div>
        <div className="metric-card">
          <p className="metric-label">In progress</p>
          <p className="metric-value">{counts?.in_progress_runs ?? "-"}</p>
        </div>
        <div className="metric-card">
          <p className="metric-label">Blocked</p>
          <p className="metric-value">{counts?.blocked_runs ?? "-"}</p>
        </div>
      </div>
      <div className="split-panels">
        <section className="glass-panel panel-stack">
          <div className="panel-heading">
            <p className="panel-eyebrow">Queue</p>
            <h2>Pending and active runs</h2>
          </div>
          <div className="trigger-bar">
            <select value={selectedFlowId} onChange={(event) => setSelectedFlowId(event.target.value)} className="control-input">
              <option value="">Select flow</option>
              {(overview?.flows ?? []).map((flow) => (
                <option key={flow.id} value={flow.id}>
                  {flow.name}
                </option>
              ))}
            </select>
            <button type="button" className="control-button" onClick={() => void triggerFlow()} disabled={!selectedFlowId}>
              Trigger Run
            </button>
          </div>
          <div className="stack-grid">
            {(runs?.runs ?? []).map((run) => (
              <button key={run.id} type="button" className="queue-row queue-row-button" onClick={() => void selectRun(run.id)}>
                <div>
                  <p className="queue-name">{run.flow_name}</p>
                  <p className="queue-meta">
                    {run.owner_agent_id} · {run.step_counts.completed}/{run.step_counts.total}
                  </p>
                </div>
                <StatusDot
                  tone={run.status === "blocked" ? "red" : run.status === "in_progress" ? "green" : "amber"}
                  label={run.status}
                />
              </button>
            ))}
          </div>
        </section>
        <section className="glass-panel panel-stack">
          <div className="panel-heading">
            <p className="panel-eyebrow">Timeline</p>
            <h2>{selectedRun?.flow.name ?? "Run detail"}</h2>
          </div>
          <HealthBar label="Completion" value={selectedRun ? Math.round((selectedRun.status_counts.completed ?? 0) / Math.max(1, selectedRun.steps.length) * 100) : 0} />
          <HealthBar label="Blocked steps" value={selectedRun ? Math.min(100, (selectedRun.status_counts.blocked ?? 0) * 25) : 0} />
          <div className="stack-grid">
            {(selectedRun?.steps ?? []).map((step) => (
              <article key={step.step_id} className="run-step-card">
                <div className="run-step-header">
                  <div>
                    <p className="metric-label">Step {step.step_order}/{maxSteps}</p>
                    <h3>{step.agent_id}</h3>
                  </div>
                  <StatusDot tone={step.status === "blocked" ? "red" : step.status === "completed" ? "green" : "amber"} label={step.status} />
                </div>
                <p className="run-step-copy">{step.objective_template}</p>
                {(step.status === "blocked" || step.status === "failed") ? (
                  <button type="button" className="control-button is-secondary" onClick={() => void retrigger(step.step_id)}>
                    Retrigger Step
                  </button>
                ) : null}
              </article>
            ))}
          </div>
          {selectedRun ? (
            <div className="field-block">
              <span>Run Context JSON</span>
              <textarea
                className="control-textarea"
                value={contextDraft}
                onChange={(event) => setContextDraft(event.target.value)}
              />
              <button type="button" className="control-button" onClick={() => void saveContext()}>
                Save Context
              </button>
            </div>
          ) : (
            <p className="panel-copy">Select a run to inspect step state and edit context.</p>
          )}
        </section>
      </div>
    </PageScaffold>
  );
}
