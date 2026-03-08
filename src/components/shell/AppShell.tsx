import { Outlet } from "react-router-dom";
import { useState } from "react";
import type { NavItem } from "../../App";
import { SlideDrawer } from "../shared/SlideDrawer";
import { ScanlineOverlay } from "../shared/ScanlineOverlay";
import { NavRail } from "./NavRail";
import { OperatorSessionPanel } from "./OperatorSessionPanel";
import { TopHUD } from "./TopHUD";

type AppShellProps = {
  navItems: NavItem[];
};

export function AppShell({ navItems }: AppShellProps) {
  const [sessionOpen, setSessionOpen] = useState(false);

  return (
    <div className="app-shell">
      <ScanlineOverlay />
      <div className="ambient-grid" aria-hidden="true" />
      <TopHUD navItems={navItems} onOpenSession={() => setSessionOpen(true)} />
      <div className="workspace-frame">
        <NavRail items={navItems} />
        <main className="content-area">
          <Outlet />
        </main>
      </div>
      <SlideDrawer
        open={sessionOpen}
        onClose={() => setSessionOpen(false)}
        title="Session Keys"
        subtitle="Frontend session headers are held only in memory for the current tab."
      >
        <OperatorSessionPanel />
      </SlideDrawer>
    </div>
  );
}
