import { requestJson } from "./client";

export type AgentSummary = {
  id: string;
  name: string;
  role: string;
  program_id?: string | null;
  program_name?: string | null;
  status: string;
  context_completeness_pct: number;
  token_estimate: number;
  missing_required_files: string[];
  kind: string;
};

export type AgentContextPayload = {
  generated_at: string;
  agent_id: string;
  agent_name: string;
  role: string;
  program_id?: string | null;
  program_name?: string | null;
  root_path: string;
  files: Array<{
    filename: string;
    present: boolean;
    stale: boolean;
    updated_at: string | null;
    token_estimate: number;
    path: string;
  }>;
  effective_context_packet: {
    token_estimate: number;
    completeness_pct: number;
  };
  missing_required_files: string[];
  links?: Record<string, string>;
};

export type FloorPayload = {
  generated_at: string;
  ian_desk?: AgentSummary;
  engineer_desk?: AgentSummary;
  program_groups: Array<{
    program_id: string;
    program_name: string;
    domain: string;
    status: string;
    masters: AgentSummary[];
    specialists: AgentSummary[];
    master_count: number;
    specialist_count: number;
    has_active_run: boolean;
  }>;
  unassigned: AgentSummary[];
  totals: {
    programs: number;
    agents: number;
    unassigned_agents: number;
  };
};

export type ProgramsOverviewPayload = {
  generated_at: string;
  agency: {
    id: string;
    label: string;
    description: string;
  };
  domains: Array<{
    domain: string;
    label: string;
    description: string;
    portfolio_role: string;
    programs: Array<{
      id: string;
      name: string;
      owner_master_id: string;
      status: string;
      apps_count: number;
      agents_count: number;
      summary: string;
      structure_badges: string[];
      active_run: boolean;
      applications: Array<{
        id: string;
        name: string;
        status: string;
        kind: string;
        health: string;
        active_agents: number;
      }>;
    }>;
  }>;
  totals: {
    domains: number;
    programs: number;
    applications: number;
  };
};

export type ProgramApplicationDetailPayload = {
  generated_at: string;
  application: {
    id: string;
    name: string;
    program_id: string;
    owner_master_id: string;
    status: string;
    kind: string;
    live_url?: string;
    notes?: string;
  };
  assigned_agents: Array<{
    id: string;
    name: string;
    status: string;
    owner_master_id: string;
  }>;
  latest_task: null | {
    id: string;
    status: string;
    objective: string;
    updated_at: string;
  };
  health_notes: string[];
};

export type AgentCoveragePayload = {
  generated_at: string;
  agents: Array<{
    agent_id: string;
    agent_name: string;
    role: string;
    program_id?: string | null;
    program_name?: string | null;
    files_present: number;
    files_missing: number;
    missing_required_count: number;
    completeness_pct: number;
    status: string;
  }>;
  totals: {
    agents: number;
    critical: number;
    complete: number;
  };
};

export type StateReportPayload = {
  generated_at: string;
  lost_vs_pending: Array<{
    feature: string;
    v1_status: string;
    v2_status: string;
    v21_target: string;
    priority: string;
    state: string;
  }>;
  api_health: Array<{
    route: string;
    status: string;
    notes: string;
  }>;
  agent_config_coverage: {
    total_agents: number;
    files_missing: number;
    critical_agents: number;
    most_common_gap: string | null;
    critical_master_agents: string[];
  };
  definition_of_done: Array<{
    id: string;
    label: string;
    checked: boolean;
  }>;
};

export type ShellHudPayload = {
  generated_at: string;
  runs_active: number;
  agents_online: number;
  last_event: string | null;
  alerts_open: number;
  clock_tz: string;
};

export function getShellHud(headers: Record<string, string>, signal?: AbortSignal) {
  return requestJson<ShellHudPayload>("/api/control-ui/shell/hud", { headers, signal });
}

export function getFloor(headers: Record<string, string>, signal?: AbortSignal) {
  return requestJson<FloorPayload>("/api/control-ui/floor", { headers, signal });
}

export function getFloorAgentDrawer(agentId: string, headers: Record<string, string>, signal?: AbortSignal) {
  return requestJson<AgentContextPayload>(`/api/control-ui/floor/agents/${encodeURIComponent(agentId)}/drawer`, {
    headers,
    signal,
  });
}

export function getProgramsOverview(headers: Record<string, string>, signal?: AbortSignal) {
  return requestJson<ProgramsOverviewPayload>("/api/control-ui/programs/overview", { headers, signal });
}

export function getProgramApplicationDetail(
  applicationId: string,
  headers: Record<string, string>,
  signal?: AbortSignal,
) {
  return requestJson<ProgramApplicationDetailPayload>(
    `/api/control-ui/programs/applications/${encodeURIComponent(applicationId)}`,
    { headers, signal },
  );
}

export function getAgentConfigs(headers: Record<string, string>, signal?: AbortSignal) {
  return requestJson<AgentCoveragePayload>("/api/control-ui/agents/configs", { headers, signal });
}

export function getAgentConfigDetail(agentId: string, headers: Record<string, string>, signal?: AbortSignal) {
  return requestJson<AgentContextPayload>(`/api/control-ui/agents/configs/${encodeURIComponent(agentId)}`, {
    headers,
    signal,
  });
}

export function getStateReport(headers: Record<string, string>, signal?: AbortSignal) {
  return requestJson<StateReportPayload>("/api/control-ui/reporting/loss-pending", { headers, signal });
}
