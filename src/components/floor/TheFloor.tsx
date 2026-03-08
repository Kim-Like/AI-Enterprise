import { useEffect, useState } from "react";
import { ApiError } from "../../lib/api/client";
import {
  getFloor,
  getFloorAgentDrawer,
  type AgentContextPayload,
  type AgentSummary,
  type FloorPayload,
} from "../../lib/api/control-ui";
import { useControlSession } from "../../lib/control-session";
import { PageScaffold } from "../shared/PageScaffold";
import { ReliabilityPips } from "../shared/ReliabilityPips";
import { SessionRequired } from "../shared/SessionRequired";
import { SlideDrawer } from "../shared/SlideDrawer";
import { StatusDot } from "../shared/StatusDot";

function toneForStatus(status: string) {
  if (status === "online" || status === "active") return "green" as const;
  if (status === "missing" || status === "error") return "red" as const;
  if (status === "queued") return "blue" as const;
  return "amber" as const;
}

export function TheFloor() {
  const { hasSession, buildHeaders } = useControlSession();
  const [data, setData] = useState<FloorPayload | null>(null);
  const [selectedAgent, setSelectedAgent] = useState<AgentContextPayload | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!hasSession) {
      setData(null);
      setError("");
      return;
    }
    let active = true;
    const controller = new AbortController();
    async function loadFloor() {
      setLoading(true);
      try {
        const payload = await getFloor(buildHeaders(), controller.signal);
        if (active) {
          setData(payload);
          setError("");
        }
      } catch (err) {
        if (active) {
          setError(err instanceof ApiError ? err.detail : "Unable to load floor state");
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }
    void loadFloor();
    return () => {
      active = false;
      controller.abort();
    };
  }, [buildHeaders, hasSession]);

  async function openAgent(agent: AgentSummary) {
    try {
      const payload = await getFloorAgentDrawer(agent.id, buildHeaders());
      setSelectedAgent(payload);
      setError("");
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Unable to load agent detail");
    }
  }

  function renderAgentCard(agent: AgentSummary) {
    const reliability = Math.max(1, Math.min(5, Math.round(agent.context_completeness_pct / 20)));
    return (
      <button
        key={agent.id}
        type="button"
        className="agent-card glass-panel"
        onClick={() => void openAgent(agent)}
      >
        <div className="agent-card-header">
          <div>
            <p className="agent-role">{agent.role}</p>
            <h2>{agent.name}</h2>
          </div>
          <StatusDot tone={toneForStatus(agent.status)} label={agent.status} />
        </div>
        <div className="agent-card-statline">
          <span>{agent.program_name || "unassigned"}</span>
          <span>{agent.kind}</span>
        </div>
        <div className="agent-card-footer">
          <ReliabilityPips score={reliability} />
          <span className="metric-inline">{agent.token_estimate} tok</span>
        </div>
      </button>
    );
  }

  return (
    <PageScaffold
      eyebrow="The Floor"
      title="Agent Presence Grid"
      description="Live roster for IAn, Engineer, program masters, and specialists, backed by the clean Phase 5 runtime."
      actions={
        <StatusDot
          tone={hasSession ? (loading ? "amber" : "green") : "red"}
          label={hasSession ? (loading ? "Loading" : "Live") : "Session required"}
        />
      }
    >
      {!hasSession ? (
        <SessionRequired detail="Open Operator Session and enter an autonomy or admin key to load the live floor roster." />
      ) : null}
      {error ? <div className="error-panel">{error}</div> : null}

      <div className="metric-grid">
        <div className="metric-card">
          <p className="metric-label">Live agents</p>
          <p className="metric-value">{data?.totals.agents ?? "-"}</p>
        </div>
        <div className="metric-card">
          <p className="metric-label">Programs</p>
          <p className="metric-value">{data?.totals.programs ?? "-"}</p>
        </div>
        <div className="metric-card">
          <p className="metric-label">Unassigned</p>
          <p className="metric-value">{data?.totals.unassigned_agents ?? "-"}</p>
        </div>
      </div>

      <div className="card-grid">
        {data?.ian_desk ? renderAgentCard(data.ian_desk) : null}
        {data?.engineer_desk ? renderAgentCard(data.engineer_desk) : null}
      </div>

      <div className="stack-grid">
        {(data?.program_groups ?? []).map((group) => (
          <section key={group.program_id} className="swimlane glass-panel">
            <div className="swimlane-header">
              <div>
                <p className="swimlane-title">{group.program_name}</p>
                <p className="swimlane-copy">{group.domain}</p>
              </div>
              <div className="swimlane-badges">
                <span className="metric-inline">{group.master_count} masters</span>
                <span className="metric-inline">{group.specialist_count} specialists</span>
                <StatusDot tone={group.has_active_run ? "green" : "dim"} label={group.has_active_run ? "Active run" : "Idle"} />
              </div>
            </div>
            <div className="card-grid compact-grid">
              {group.masters.map(renderAgentCard)}
              {group.specialists.map(renderAgentCard)}
            </div>
          </section>
        ))}
      </div>

      <SlideDrawer
        open={Boolean(selectedAgent)}
        onClose={() => setSelectedAgent(null)}
        title={selectedAgent?.agent_name ?? "Agent"}
        subtitle={selectedAgent?.role}
      >
        <div className="drawer-stack">
          <div className="metric-card">
            <p className="metric-label">Context completeness</p>
            <p className="metric-value">{selectedAgent?.effective_context_packet.completeness_pct ?? 0}%</p>
          </div>
          <div className="metric-card">
            <p className="metric-label">Token estimate</p>
            <p className="metric-value">{selectedAgent?.effective_context_packet.token_estimate ?? 0}</p>
          </div>
          <div className="table-shell glass-panel">
            <table>
              <thead>
                <tr>
                  <th>File</th>
                  <th>Present</th>
                  <th>Stale</th>
                </tr>
              </thead>
              <tbody>
                {(selectedAgent?.files ?? []).map((file) => (
                  <tr key={file.filename}>
                    <td>{file.filename}</td>
                    <td>{file.present ? "yes" : "no"}</td>
                    <td>{file.stale ? "yes" : "no"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </SlideDrawer>
    </PageScaffold>
  );
}
