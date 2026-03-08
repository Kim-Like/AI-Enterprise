import { useEffect, useState } from "react";
import { ApiError } from "../../lib/api/client";
import { getStateReport, type StateReportPayload } from "../../lib/api/control-ui";
import { useControlSession } from "../../lib/control-session";
import { PageScaffold } from "../shared/PageScaffold";
import { SessionRequired } from "../shared/SessionRequired";
import { StatusDot } from "../shared/StatusDot";

export function StateReport() {
  const { hasSession, buildHeaders } = useControlSession();
  const [data, setData] = useState<StateReportPayload | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!hasSession) {
      setData(null);
      return;
    }
    let active = true;
    const controller = new AbortController();
    void getStateReport(buildHeaders(), controller.signal)
      .then((payload) => {
        if (active) {
          setData(payload);
          setError("");
        }
      })
      .catch((err) => {
        if (active) {
          setError(err instanceof ApiError ? err.detail : "Unable to load report");
        }
      });
    return () => {
      active = false;
      controller.abort();
    };
  }, [buildHeaders, hasSession]);

  return (
    <PageScaffold
      eyebrow="Report"
      title="State Readiness Board"
      description="A compressed view of route readiness, coverage drift, and definition-of-done status from the clean backend."
    >
      {!hasSession ? (
        <SessionRequired detail="Open Operator Session to load the live state report." />
      ) : null}
      {error ? <div className="error-panel">{error}</div> : null}
      <div className="stack-grid">
        {(data?.definition_of_done ?? []).map((check) => (
          <article key={check.id} className="glass-panel checklist-card">
            <div>
              <p className="metric-label">Definition of done</p>
              <h2>{check.label}</h2>
            </div>
            <StatusDot tone={check.checked ? "green" : "amber"} label={check.checked ? "ready" : "pending"} />
          </article>
        ))}
      </div>
      <div className="table-shell glass-panel">
        <table>
          <thead>
            <tr>
              <th>Feature</th>
              <th>V1</th>
              <th>V2</th>
              <th>Target</th>
            </tr>
          </thead>
          <tbody>
            {(data?.lost_vs_pending ?? []).map((row) => (
              <tr key={row.feature}>
                <td>{row.feature}</td>
                <td>{row.v1_status}</td>
                <td>{row.v2_status}</td>
                <td>{row.v21_target}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </PageScaffold>
  );
}
