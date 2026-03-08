import { useControlSession } from "../../lib/control-session";

export function OperatorSessionPanel() {
  const { adminKey, autonomyKey, setAdminKey, setAutonomyKey, clearSession, hasSession } =
    useControlSession();

  return (
    <div className="session-panel">
      <div className="metric-grid">
        <div className="metric-card">
          <p className="metric-label">Policy</p>
          <p className="metric-value">In-memory only</p>
        </div>
        <div className="metric-card">
          <p className="metric-label">Persistence</p>
          <p className="metric-value">None</p>
        </div>
        <div className="metric-card">
          <p className="metric-label">Session State</p>
          <p className="metric-value">{hasSession ? "Armed" : "Idle"}</p>
        </div>
      </div>

      <label className="field-block">
        <span>Admin Key</span>
        <input
          type="password"
          value={adminKey}
          onChange={(event) => setAdminKey(event.target.value)}
          placeholder="X-Admin-Key"
        />
      </label>

      <label className="field-block">
        <span>Autonomy Key</span>
        <input
          type="password"
          value={autonomyKey}
          onChange={(event) => setAutonomyKey(event.target.value)}
          placeholder="X-Autonomy-Key"
        />
      </label>

      <div className="session-callout">
        This panel is intentionally ephemeral. Closing or refreshing the tab drops the session keys.
      </div>

      <button type="button" className="control-button is-secondary" onClick={clearSession}>
        Clear Session
      </button>
    </div>
  );
}
