import { useEffect, useState } from "react";
import { ApiError } from "../../lib/api/client";
import { getSecretStatus, testSecretTarget, type SecretStatusPayload, type SecretTestPayload } from "../../lib/api/secrets";
import { useControlSession } from "../../lib/control-session";
import { PageScaffold } from "../shared/PageScaffold";
import { SessionRequired } from "../shared/SessionRequired";
import { StatusDot } from "../shared/StatusDot";

export function SecretsPanel() {
  const { hasSession, hasAdminSession, buildHeaders } = useControlSession();
  const [data, setData] = useState<SecretStatusPayload | null>(null);
  const [result, setResult] = useState<SecretTestPayload | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!hasSession) {
      setData(null);
      return;
    }
    let active = true;
    const controller = new AbortController();
    void getSecretStatus(buildHeaders(), controller.signal)
      .then((payload) => {
        if (active) {
          setData(payload);
          setError("");
        }
      })
      .catch((err) => {
        if (active) {
          setError(err instanceof ApiError ? err.detail : "Unable to load secret status");
        }
      });
    return () => {
      active = false;
      controller.abort();
    };
  }, [buildHeaders, hasSession]);

  async function runTest(target: string) {
    try {
      const payload = await testSecretTarget(target, buildHeaders());
      setResult(payload);
      setError("");
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Unable to test connection");
    }
  }

  return (
    <PageScaffold
      eyebrow="Secrets"
      title="Connection Status Surface"
      description="Redacted secret inventory and connection status from the clean backend, with live test actions gated to admin sessions."
      actions={<StatusDot tone="red" label="No values exposed" />}
    >
      {!hasSession ? (
        <SessionRequired detail="Open Operator Session to inspect secret presence and connection status." />
      ) : null}
      {error ? <div className="error-panel">{error}</div> : null}
      <div className="metric-grid">
        <div className="metric-card">
          <p className="metric-label">Present</p>
          <p className="metric-value">{data?.summary.present ?? "-"}</p>
        </div>
        <div className="metric-card">
          <p className="metric-label">Missing</p>
          <p className="metric-value">{data?.summary.missing ?? "-"}</p>
        </div>
        <div className="metric-card">
          <p className="metric-label">Live connections</p>
          <p className="metric-value">{data?.summary.connections_live ?? "-"}</p>
        </div>
      </div>
      <div className="table-shell glass-panel">
        <table>
          <thead>
            <tr>
              <th>Target</th>
              <th>Status</th>
              <th>Evidence</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {(data?.connections ?? []).map((row) => (
              <tr key={row.target}>
                <td>{row.label}</td>
                <td>{row.status}</td>
                <td>{row.evidence}</td>
                <td>
                  <button
                    type="button"
                    className="table-action"
                    onClick={() => void runTest(row.target)}
                    disabled={!hasAdminSession}
                  >
                    Test
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {result ? (
        <div className="note-panel">
          Last test: {result.result.label} {"->"} {result.result.status} ({result.result.evidence})
        </div>
      ) : null}
    </PageScaffold>
  );
}
