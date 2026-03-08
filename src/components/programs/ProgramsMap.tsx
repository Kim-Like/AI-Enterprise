import { useEffect, useState } from "react";
import { ApiError } from "../../lib/api/client";
import {
  getProgramApplicationDetail,
  getProgramsOverview,
  type ProgramApplicationDetailPayload,
  type ProgramsOverviewPayload,
} from "../../lib/api/control-ui";
import { useControlSession } from "../../lib/control-session";
import { PageScaffold } from "../shared/PageScaffold";
import { SessionRequired } from "../shared/SessionRequired";
import { SlideDrawer } from "../shared/SlideDrawer";
import { StatusDot } from "../shared/StatusDot";

export function ProgramsMap() {
  const { hasSession, buildHeaders } = useControlSession();
  const [data, setData] = useState<ProgramsOverviewPayload | null>(null);
  const [detail, setDetail] = useState<ProgramApplicationDetailPayload | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!hasSession) {
      setData(null);
      return;
    }
    let active = true;
    const controller = new AbortController();
    void getProgramsOverview(buildHeaders(), controller.signal)
      .then((payload) => {
        if (active) {
          setData(payload);
          setError("");
        }
      })
      .catch((err) => {
        if (active) {
          setError(err instanceof ApiError ? err.detail : "Unable to load programs");
        }
      });
    return () => {
      active = false;
      controller.abort();
    };
  }, [buildHeaders, hasSession]);

  async function openApplication(applicationId: string) {
    try {
      const payload = await getProgramApplicationDetail(applicationId, buildHeaders());
      setDetail(payload);
      setError("");
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Unable to load application detail");
    }
  }

  return (
    <PageScaffold
      eyebrow="Programs"
      title="Portfolio Swimlanes"
      description="Domain portfolio map backed by the duplicated registry and application projections."
      actions={<StatusDot tone={hasSession ? "green" : "red"} label={hasSession ? "Live" : "Session required"} />}
    >
      {!hasSession ? (
        <SessionRequired detail="Open Operator Session to load the live program and application registry." />
      ) : null}
      {error ? <div className="error-panel">{error}</div> : null}
      <div className="swimlane-stack">
        {data?.agency ? (
          <section className="metric-card glass-panel portfolio-header">
            <div>
              <p className="program-node-eyebrow">Governing Layer</p>
              <h2>{data.agency.label}</h2>
              <p className="portfolio-summary">{data.agency.description}</p>
            </div>
            <div className="badge-row">
              <span className="metric-inline">{data.totals.programs} programs</span>
              <span className="metric-inline">{data.totals.applications} applications</span>
            </div>
          </section>
        ) : null}
        {(data?.domains ?? []).map((domain) => (
          <section key={domain.domain} className="swimlane glass-panel">
            <div className="swimlane-header">
              <div>
                <p className="swimlane-title">{domain.label}</p>
                <p className="swimlane-copy">{domain.description}</p>
              </div>
              <div className="swimlane-meta">
                <span className="metric-inline">{domain.portfolio_role}</span>
                <span className="metric-inline">{domain.programs.length} programs</span>
              </div>
            </div>
            <div className="swimlane-content">
              {domain.programs.map((program) => (
                <article key={program.id} className="program-node">
                  <p className="program-node-eyebrow">Program</p>
                  <h2>{program.name}</h2>
                  <p className="program-node-copy">
                    {program.owner_master_id} · {program.apps_count} applications · {program.agents_count} agents
                  </p>
                  <p className="portfolio-summary">{program.summary}</p>
                  <div className="badge-row">
                    {program.structure_badges.map((badge) => (
                      <span key={badge} className="tag-chip">
                        {badge}
                      </span>
                    ))}
                  </div>
                  <div className="app-pill-row">
                    {program.applications.map((app) => (
                      <button
                        key={app.id}
                        type="button"
                        className={`app-pill app-pill-${app.health}`}
                        onClick={() => void openApplication(app.id)}
                      >
                        {app.name}
                      </button>
                    ))}
                  </div>
                </article>
              ))}
            </div>
          </section>
        ))}
      </div>
      <SlideDrawer
        open={Boolean(detail)}
        onClose={() => setDetail(null)}
        title={detail?.application.name ?? "Application"}
        subtitle={detail?.application.id}
      >
        <div className="drawer-stack">
          <div className="metric-card">
            <p className="metric-label">Status</p>
            <p className="metric-value">{detail?.application.status ?? "-"}</p>
          </div>
          <div className="metric-card">
            <p className="metric-label">Assigned agents</p>
            <p className="metric-value">{detail?.assigned_agents.length ?? 0}</p>
          </div>
          <div className="stack-grid">
            {(detail?.health_notes ?? []).map((note) => (
              <div key={note} className="note-panel">
                {note}
              </div>
            ))}
          </div>
        </div>
      </SlideDrawer>
    </PageScaffold>
  );
}
