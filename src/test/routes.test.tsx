import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { AppRoutes } from "../App";
import { ControlSessionProvider } from "../lib/control-session";

function renderApp(path: string, options?: { adminKey?: string; autonomyKey?: string }) {
  return render(
    <ControlSessionProvider
      initialAdminKey={options?.adminKey ?? ""}
      initialAutonomyKey={options?.autonomyKey ?? "auto-write"}
    >
      <MemoryRouter
        initialEntries={[path]}
        future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
      >
        <AppRoutes />
      </MemoryRouter>
    </ControlSessionProvider>,
  );
}

function jsonResponse(payload: unknown) {
  return Promise.resolve(
    new Response(JSON.stringify(payload), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    }),
  );
}

function setupFetchMock() {
  return vi.spyOn(globalThis, "fetch").mockImplementation((input, init) => {
    const url = typeof input === "string" ? input : input.toString();
    const method = init?.method ?? "GET";

    if (url === "/api/control-ui/shell/hud") {
      return jsonResponse({
        generated_at: "2026-03-08T00:00:00Z",
        runs_active: 2,
        agents_online: 8,
        last_event: "2026-03-08T00:00:00Z",
        alerts_open: 1,
        clock_tz: "Europe/Copenhagen",
      });
    }

    if (url === "/api/control-ui/floor") {
      return jsonResponse({
        generated_at: "2026-03-08T00:00:00Z",
        ian_desk: {
          id: "father",
          name: "IAn",
          role: "father",
          program_name: "AI Enterprise",
          status: "online",
          context_completeness_pct: 100,
          token_estimate: 1200,
          missing_required_files: [],
          kind: "master",
        },
        engineer_desk: {
          id: "engineer",
          name: "Engineer",
          role: "lead",
          program_name: "AI Enterprise",
          status: "online",
          context_completeness_pct: 100,
          token_estimate: 900,
          missing_required_files: [],
          kind: "master",
        },
        program_groups: [
          {
            program_id: "artisan-reporting",
            program_name: "Artisan Reporting",
            domain: "artisan",
            status: "active",
            masters: [
              {
                id: "artisan-master",
                name: "Artisan Master",
                role: "master",
                program_name: "Artisan Reporting",
                status: "online",
                context_completeness_pct: 85,
                token_estimate: 600,
                missing_required_files: ["heartbeat.md"],
                kind: "master",
              },
            ],
            specialists: [],
            master_count: 1,
            specialist_count: 0,
            has_active_run: true,
          },
        ],
        unassigned: [],
        totals: { programs: 10, agents: 44, unassigned_agents: 0 },
      });
    }

    if (url.startsWith("/api/control-ui/floor/agents/")) {
      return jsonResponse({
        generated_at: "2026-03-08T00:00:00Z",
        agent_id: "father",
        agent_name: "IAn",
        role: "father",
        program_name: "AI Enterprise",
        root_path: "/agents/IAn",
        files: [{ filename: "soul.md", present: true, stale: false, updated_at: "2026-03-08T00:00:00Z", token_estimate: 10, path: "/agents/IAn/soul.md" }],
        effective_context_packet: { token_estimate: 100, completeness_pct: 100 },
        missing_required_files: [],
      });
    }

    if (url === "/api/control-ui/programs/overview") {
      return jsonResponse({
        generated_at: "2026-03-08T00:00:00Z",
        agency: {
          id: "ian-agency",
          label: "IAn Agency",
          description: "Main agent program and governing layer for the operational portfolio.",
        },
        domains: [
          {
            domain: "artisan",
            label: "Artisan",
            description: "Reporting, WordPress commerce, and campaign operations.",
            portfolio_role: "program",
            programs: [
              {
                id: "artisan-reporting",
                name: "Artisan Reporting",
                owner_master_id: "artisan-master",
                status: "active",
                apps_count: 1,
                agents_count: 3,
                summary: "Billy-backed reporting workflows and accounting operations.",
                structure_badges: ["reporting", "billy", "cpanel"],
                active_run: true,
                applications: [
                  {
                    id: "artisan-reporting-app",
                    name: "Artisan Reporting App",
                    status: "active",
                    kind: "dashboard",
                    health: "green",
                    active_agents: 2,
                  },
                ],
              },
            ],
          },
        ],
        totals: { domains: 1, programs: 1, applications: 1 },
      });
    }

    if (url === "/api/control-ui/programs/applications/artisan-reporting-app") {
      return jsonResponse({
        generated_at: "2026-03-08T00:00:00Z",
        application: {
          id: "artisan-reporting-app",
          name: "Artisan Reporting App",
          program_id: "artisan-reporting",
          owner_master_id: "artisan-master",
          status: "active",
          kind: "dashboard",
        },
        assigned_agents: [{ id: "gov.ian-mission-control", name: "Governor", status: "active", owner_master_id: "father" }],
        latest_task: { id: "task-1", status: "completed", objective: "Refresh report", updated_at: "2026-03-08T00:00:00Z" },
        health_notes: ["No immediate risk markers detected."],
      });
    }

    if (url === "/api/control-ui/orchestration/overview") {
      return jsonResponse({
        generated_at: "2026-03-08T00:00:00Z",
        counts: { active_sessions: 1, total_flows: 1, active_flows: 1, in_progress_runs: 1, queued_runs: 0, blocked_runs: 0 },
        health: { open_escalations: 0, open_errors: 0 },
        flows: [
          {
            id: "flow-1",
            owner_agent_id: "engineer",
            program_id: "ian-control-plane",
            name: "Nightly Control Loop",
            description: "",
            execution_mode: "locked_pipeline",
            schedule_kind: "manual",
            schedule_expr: "",
            status: "active",
            created_by: "test",
            created_at: "2026-03-08T00:00:00Z",
            updated_at: "2026-03-08T00:00:00Z",
          },
        ],
        sessions: [],
        recent_runs: [],
      });
    }

    if (url === "/api/control-ui/orchestration/runs") {
      return jsonResponse({
        generated_at: "2026-03-08T00:00:00Z",
        runs: [
          {
            id: "run-1",
            flow_id: "flow-1",
            flow_name: "Nightly Control Loop",
            owner_agent_id: "engineer",
            program_id: "ian-control-plane",
            status: "in_progress",
            trigger_type: "manual",
            triggered_by: "workspace-ui",
            run_context_json: {},
            created_at: "2026-03-08T00:00:00Z",
            step_counts: { total: 2, queued: 1, in_progress: 1, completed: 0, failed: 0, blocked: 0 },
          },
        ],
        filters: { limit: 200 },
        totals: { runs: 1, in_progress: 1, blocked: 0, completed: 0 },
      });
    }

    if (url === "/api/control-ui/orchestration/runs/run-1" || url === "/api/control-ui/orchestration/runs/run-2") {
      return jsonResponse({
        generated_at: "2026-03-08T00:00:00Z",
        run: {
          id: url.endsWith("run-2") ? "run-2" : "run-1",
          flow_id: "flow-1",
          trigger_type: "manual",
          triggered_by: "workspace-ui",
          status: "in_progress",
          run_context_json: {},
          created_at: "2026-03-08T00:00:00Z",
        },
        flow: {
          id: "flow-1",
          owner_agent_id: "engineer",
          program_id: "ian-control-plane",
          name: "Nightly Control Loop",
          description: "",
          execution_mode: "locked_pipeline",
          schedule_kind: "manual",
          schedule_expr: "",
          status: "active",
          created_by: "test",
          created_at: "2026-03-08T00:00:00Z",
          updated_at: "2026-03-08T00:00:00Z",
        },
        steps: [
          {
            id: "row-1",
            run_id: "run-1",
            step_id: "step-1",
            task_id: "task-1",
            status: "in_progress",
            output_valid: 0,
            step_order: 1,
            agent_id: "spec.engineer.orchestration",
            objective_template: "Route program state",
            input_contract_json: {},
            output_schema_json: {},
            retry_policy_json: {},
            on_failure: "escalate",
            timeout_seconds: 120,
          },
        ],
        status_counts: { in_progress: 1 },
      });
    }

    if (url === "/api/control-ui/orchestration/trigger" && method === "POST") {
      return jsonResponse({
        generated_at: "2026-03-08T00:00:00Z",
        run: {
          id: "run-2",
          flow_id: "flow-1",
          trigger_type: "manual",
          triggered_by: "workspace-ui",
          status: "in_progress",
          run_context_json: {},
          created_at: "2026-03-08T00:00:00Z",
        },
        flow: {
          id: "flow-1",
          owner_agent_id: "engineer",
          program_id: "ian-control-plane",
          name: "Nightly Control Loop",
          description: "",
          execution_mode: "locked_pipeline",
          schedule_kind: "manual",
          schedule_expr: "",
          status: "active",
          created_by: "test",
          created_at: "2026-03-08T00:00:00Z",
          updated_at: "2026-03-08T00:00:00Z",
        },
        steps: [],
        status_counts: { in_progress: 1 },
      });
    }

    if (url === "/api/orchestration/runs/run-1/context" && method === "PATCH") {
      return jsonResponse({
        run: { id: "run-1", run_context_json: { saved: true } },
        flow: { id: "flow-1", name: "Nightly Control Loop" },
        steps: [],
        status_counts: { in_progress: 1 },
      });
    }

    if (url === "/api/orchestration/runs/run-1/steps/step-1/retrigger" && method === "POST") {
      return jsonResponse({
        run: { id: "run-1", run_context_json: {} },
        flow: { id: "flow-1", name: "Nightly Control Loop" },
        steps: [],
        status_counts: { in_progress: 1 },
        retriggered_step: { step_id: "step-1", new_task_id: "task-2", previous_task_id: "task-1", triggered_by: "workspace-ui" },
      });
    }

    if (url === "/api/control-ui/agents/configs") {
      return jsonResponse({
        generated_at: "2026-03-08T00:00:00Z",
        agents: [
          {
            agent_id: "father",
            agent_name: "IAn",
            role: "father",
            files_present: 8,
            files_missing: 0,
            missing_required_count: 0,
            completeness_pct: 100,
            status: "online",
          },
        ],
        totals: { agents: 1, critical: 0, complete: 1 },
      });
    }

    if (url === "/api/control-ui/agents/configs/father") {
      return jsonResponse({
        generated_at: "2026-03-08T00:00:00Z",
        agent_id: "father",
        agent_name: "IAn",
        role: "father",
        program_name: "AI Enterprise",
        root_path: "/agents/IAn",
        files: [{ filename: "soul.md", present: true, stale: false, updated_at: "2026-03-08T00:00:00Z", token_estimate: 10, path: "/agents/IAn/soul.md" }],
        effective_context_packet: { token_estimate: 100, completeness_pct: 100 },
        missing_required_files: [],
      });
    }

    if (url === "/api/control-ui/reporting/loss-pending") {
      return jsonResponse({
        generated_at: "2026-03-08T00:00:00Z",
        lost_vs_pending: [{ feature: "Normalized agent roster", v1_status: "legacy", v2_status: "partial", v21_target: "active", priority: "P0", state: "healthy" }],
        api_health: [{ route: "/api/control-ui/agents", status: "active", notes: "Phase 5 required route" }],
        agent_config_coverage: { total_agents: 44, files_missing: 2, critical_agents: 1, most_common_gap: "heartbeat.md", critical_master_agents: ["Artisan Master"] },
        definition_of_done: [{ id: "routes", label: "Normalized control-plane read routes exist", checked: true }],
      });
    }

    if (url === "/api/control-ui/secrets/status") {
      return jsonResponse({
        status: "ok",
        checked_at: "2026-03-08T00:00:00Z",
        summary: { present: 2, missing: 1, invalid: 0, connections_live: 1, connections_partial: 1, connections_missing: 0, connections_planned: 0 },
        secrets: [],
        connections: [{ target: "cpanel-ssh", label: "cPanel SSH", provider: "cPanel", status: "live", evidence: "ssh_handshake_ok", checked_at: "2026-03-08T00:00:00Z" }],
        datastores: [],
      });
    }

    if (url === "/api/control-ui/secrets/test/cpanel-ssh" && method === "POST") {
      return jsonResponse({
        status: "ok",
        result: { target: "cpanel-ssh", label: "cPanel SSH", provider: "cPanel", status: "live", evidence: "ssh_handshake_ok", checked_at: "2026-03-08T00:00:00Z" },
      });
    }

    if (url === "/api/settings") {
      return jsonResponse([
        { key: "theme_density", value: "dense", description: "UI density preset", updated_at: "2026-03-08T00:00:00Z" },
      ]);
    }

    if (url === "/api/settings/theme_density" && method === "PUT") {
      return jsonResponse({ key: "theme_density", value: "dense" });
    }

    return Promise.reject(new Error(`Unhandled fetch: ${method} ${url}`));
  });
}

describe("route surfaces", () => {
  test("routes render live data-backed floor, programs, and configs", async () => {
    const fetchMock = setupFetchMock();
    const user = userEvent.setup();

    const floor = renderApp("/");
    expect(await screen.findByRole("heading", { name: "Agent Presence Grid" })).toBeInTheDocument();
    expect(await screen.findByText("Artisan Master")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /ian/i }));
    expect(await screen.findByText("Context completeness")).toBeInTheDocument();
    floor.unmount();

    const programs = renderApp("/programs");
    expect(await screen.findByRole("heading", { name: "Portfolio Swimlanes" })).toBeInTheDocument();
    expect(await screen.findByText("IAn Agency")).toBeInTheDocument();
    expect(await screen.findByText("Reporting, WordPress commerce, and campaign operations.")).toBeInTheDocument();
    expect(await screen.findByRole("button", { name: /artisan reporting app/i })).toBeInTheDocument();
    expect(await screen.findByText("reporting")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /artisan reporting app/i }));
    expect(await screen.findByText(/No immediate risk markers detected/i)).toBeInTheDocument();
    programs.unmount();

    renderApp("/agents/configs/father");
    expect(await screen.findByRole("heading", { name: "Canonical File Health" })).toBeInTheDocument();
    expect(await screen.findByRole("heading", { name: "IAn" })).toBeInTheDocument();
    expect(await screen.findByText("soul.md")).toBeInTheDocument();

    fetchMock.mockRestore();
  });

  test("routes wire orchestration, reporting, secrets, and settings data", async () => {
    const fetchMock = setupFetchMock();
    const user = userEvent.setup();

    const orchestration = renderApp("/orchestration", { adminKey: "real-admin-key", autonomyKey: "auto-write" });
    expect(await screen.findByRole("heading", { name: "Run Queue And Timeline" })).toBeInTheDocument();
    expect(await screen.findByRole("option", { name: "Nightly Control Loop" })).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /trigger run/i }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith("/api/control-ui/orchestration/trigger", expect.any(Object)));
    orchestration.unmount();

    const report = renderApp("/report");
    expect(await screen.findByText("Normalized agent roster")).toBeInTheDocument();
    report.unmount();

    const secrets = renderApp("/secrets", { adminKey: "real-admin-key", autonomyKey: "auto-write" });
    expect(await screen.findByText("cPanel SSH")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /test/i }));
    expect(await screen.findByText(/Last test: cPanel SSH/i)).toBeInTheDocument();
    secrets.unmount();

    renderApp("/settings", { adminKey: "real-admin-key", autonomyKey: "auto-write" });
    expect(await screen.findByDisplayValue("dense")).toBeInTheDocument();

    fetchMock.mockRestore();
  });
});
