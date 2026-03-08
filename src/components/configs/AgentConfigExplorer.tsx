import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { ApiError } from "../../lib/api/client";
import {
  getAgentConfigDetail,
  getAgentConfigs,
  type AgentContextPayload,
  type AgentCoveragePayload,
} from "../../lib/api/control-ui";
import { useControlSession } from "../../lib/control-session";
import { PageScaffold } from "../shared/PageScaffold";
import { SessionRequired } from "../shared/SessionRequired";
import { SlideDrawer } from "../shared/SlideDrawer";

export function AgentConfigExplorer() {
  const { agentId } = useParams();
  const { hasSession, buildHeaders } = useControlSession();
  const [data, setData] = useState<AgentCoveragePayload | null>(null);
  const [detail, setDetail] = useState<AgentContextPayload | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!hasSession) {
      setData(null);
      return;
    }
    let active = true;
    const controller = new AbortController();
    void getAgentConfigs(buildHeaders(), controller.signal)
      .then((payload) => {
        if (active) {
          setData(payload);
          setError("");
        }
      })
      .catch((err) => {
        if (active) {
          setError(err instanceof ApiError ? err.detail : "Unable to load agent configs");
        }
      });
    return () => {
      active = false;
      controller.abort();
    };
  }, [buildHeaders, hasSession]);

  useEffect(() => {
    if (!hasSession || !agentId) {
      return;
    }
    void openDetail(agentId);
  }, [agentId, hasSession]);

  async function openDetail(targetAgentId: string) {
    try {
      const payload = await getAgentConfigDetail(targetAgentId, buildHeaders());
      setDetail(payload);
      setError("");
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Unable to load canonical files");
    }
  }

  return (
    <PageScaffold
      eyebrow="Agent Configs"
      title="Canonical File Health"
      description="A live audit table for canonical file coverage, staleness, and context completeness."
    >
      {!hasSession ? (
        <SessionRequired detail="Open Operator Session to audit canonical files across the duplicated agent hierarchy." />
      ) : null}
      {error ? <div className="error-panel">{error}</div> : null}
      <div className="table-shell glass-panel">
        <table>
          <thead>
            <tr>
              <th>Agent</th>
              <th>Files Present</th>
              <th>Missing</th>
              <th>Role</th>
            </tr>
          </thead>
          <tbody>
            {(data?.agents ?? []).map((row) => (
              <tr key={row.agent_id} className="clickable-row" onClick={() => void openDetail(row.agent_id)}>
                <td>{row.agent_name}</td>
                <td>{row.files_present}/8</td>
                <td>{row.files_missing}</td>
                <td>{row.role}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <SlideDrawer
        open={Boolean(detail)}
        onClose={() => setDetail(null)}
        title={detail?.agent_name ?? "Agent"}
        subtitle={detail?.role}
      >
        <div className="drawer-stack">
          <div className="metric-card">
            <p className="metric-label">Program</p>
            <p className="metric-value">{detail?.program_name ?? "-"}</p>
          </div>
          <div className="table-shell glass-panel">
            <table>
              <thead>
                <tr>
                  <th>File</th>
                  <th>Present</th>
                  <th>Updated</th>
                </tr>
              </thead>
              <tbody>
                {(detail?.files ?? []).map((file) => (
                  <tr key={file.filename}>
                    <td>{file.filename}</td>
                    <td>{file.present ? "yes" : "no"}</td>
                    <td>{file.updated_at ?? "-"}</td>
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
