import { useEffect, useState } from "react";
import { ApiError } from "../../lib/api/client";
import { getSettings, updateSetting, type SettingRow } from "../../lib/api/settings";
import { useControlSession } from "../../lib/control-session";
import { PageScaffold } from "../shared/PageScaffold";
import { SessionRequired } from "../shared/SessionRequired";

export function SystemSettings() {
  const { hasAdminSession, buildHeaders } = useControlSession();
  const [settings, setSettings] = useState<SettingRow[]>([]);
  const [drafts, setDrafts] = useState<Record<string, string>>({});
  const [error, setError] = useState("");

  useEffect(() => {
    if (!hasAdminSession) {
      setSettings([]);
      return;
    }
    let active = true;
    const controller = new AbortController();
    void getSettings(buildHeaders(), controller.signal)
      .then((payload) => {
        if (active) {
          setSettings(payload);
          setDrafts(
            payload.reduce<Record<string, string>>((acc, item) => {
              acc[item.key] = item.value;
              return acc;
            }, {}),
          );
          setError("");
        }
      })
      .catch((err) => {
        if (active) {
          setError(err instanceof ApiError ? err.detail : "Unable to load settings");
        }
      });
    return () => {
      active = false;
      controller.abort();
    };
  }, [buildHeaders, hasAdminSession]);

  async function saveSetting(row: SettingRow) {
    try {
      await updateSetting(
        row.key,
        {
          value: drafts[row.key] ?? row.value,
          description: row.description,
        },
        buildHeaders(),
      );
      const refreshed = await getSettings(buildHeaders());
      setSettings(refreshed);
      setError("");
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Unable to save setting");
    }
  }

  return (
    <PageScaffold
      eyebrow="Settings"
      title="System Preferences"
      description="Admin-only backend settings for the clean target runtime."
    >
      {!hasAdminSession ? (
        <SessionRequired title="Admin Session Required" detail="Enter a valid admin key to inspect and change backend settings." />
      ) : null}
      {error ? <div className="error-panel">{error}</div> : null}
      <div className="stack-grid">
        {settings.map((row) => (
          <div key={row.key} className="glass-panel setting-row">
            <div className="setting-row-head">
              <div>
                <p className="metric-label">{row.key}</p>
                <p className="setting-description">{row.description || "No description"}</p>
              </div>
              <button type="button" className="control-button is-secondary" onClick={() => void saveSetting(row)}>
                Save
              </button>
            </div>
            <input
              className="control-input"
              value={drafts[row.key] ?? ""}
              onChange={(event) =>
                setDrafts((current) => ({
                  ...current,
                  [row.key]: event.target.value,
                }))
              }
            />
          </div>
        ))}
      </div>
    </PageScaffold>
  );
}
