import { Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "./components/shell/AppShell";
import { AgentConfigExplorer } from "./components/configs/AgentConfigExplorer";
import { TheFloor } from "./components/floor/TheFloor";
import { OrchestrationCenter } from "./components/orchestration/OrchestrationCenter";
import { ProgramsMap } from "./components/programs/ProgramsMap";
import { StateReport } from "./components/report/StateReport";
import { SecretsPanel } from "./components/secrets/SecretsPanel";
import { SystemSettings } from "./components/settings/SystemSettings";

export type NavItem = {
  to: string;
  label: string;
  shortLabel: string;
  eyebrow: string;
};

export const NAV_ITEMS: NavItem[] = [
  { to: "/", label: "The Floor", shortLabel: "Floor", eyebrow: "Roster" },
  { to: "/programs", label: "Programs", shortLabel: "Programs", eyebrow: "Portfolio" },
  { to: "/orchestration", label: "Orchestration", shortLabel: "Flows", eyebrow: "Control" },
  { to: "/agents/configs", label: "Agent Configs", shortLabel: "Configs", eyebrow: "Canonical" },
  { to: "/report", label: "State Report", shortLabel: "Report", eyebrow: "Readiness" },
  { to: "/secrets", label: "Secrets", shortLabel: "Secrets", eyebrow: "Security" },
  { to: "/settings", label: "Settings", shortLabel: "Settings", eyebrow: "System" },
];

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<AppShell navItems={NAV_ITEMS} />}>
        <Route path="/" element={<TheFloor />} />
        <Route path="/programs" element={<ProgramsMap />} />
        <Route path="/orchestration" element={<OrchestrationCenter />} />
        <Route path="/orchestration-center" element={<Navigate to="/orchestration" replace />} />
        <Route path="/agents/configs" element={<AgentConfigExplorer />} />
        <Route path="/agents/configs/:agentId" element={<AgentConfigExplorer />} />
        <Route path="/report" element={<StateReport />} />
        <Route path="/secrets" element={<SecretsPanel />} />
        <Route path="/settings" element={<SystemSettings />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
