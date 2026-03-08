import { useEffect, useMemo, useState } from "react";
import { useLocation } from "react-router-dom";
import type { NavItem } from "../../App";
import { useControlSession } from "../../lib/control-session";
import { getShellHud, type ShellHudPayload } from "../../lib/api/control-ui";
import { HealthBar } from "../shared/HealthBar";
import { ReliabilityPips } from "../shared/ReliabilityPips";
import { StatusDot } from "../shared/StatusDot";

type TopHUDProps = {
  navItems: NavItem[];
  onOpenSession: () => void;
};

export function TopHUD({ navItems, onOpenSession }: TopHUDProps) {
  const location = useLocation();
  const { hasSession, buildHeaders } = useControlSession();
  const [clock, setClock] = useState(() =>
    new Intl.DateTimeFormat("en-GB", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
      timeZone: "Europe/Copenhagen",
    }).format(new Date()),
  );

  useEffect(() => {
    const timer = window.setInterval(() => {
      setClock(
        new Intl.DateTimeFormat("en-GB", {
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
          hour12: false,
          timeZone: "Europe/Copenhagen",
        }).format(new Date()),
      );
    }, 1000);
    return () => window.clearInterval(timer);
  }, []);

  const [hud, setHud] = useState<ShellHudPayload | null>(null);

  useEffect(() => {
    if (!hasSession) {
      setHud(null);
      return;
    }
    let active = true;
    const controller = new AbortController();
    async function loadHud() {
      try {
        const payload = await getShellHud(buildHeaders(), controller.signal);
        if (active) {
          setHud(payload);
        }
      } catch {
        if (active) {
          setHud(null);
        }
      }
    }
    void loadHud();
    const timer = window.setInterval(() => {
      void loadHud();
    }, 15000);
    return () => {
      active = false;
      controller.abort();
      window.clearInterval(timer);
    };
  }, [buildHeaders, hasSession]);

  const active = useMemo(
    () =>
      navItems.find((item) => {
        if (item.to === "/") {
          return location.pathname === "/";
        }
        return location.pathname.startsWith(item.to);
      }) ?? navItems[0],
    [location.pathname, navItems],
  );

  return (
    <header className="top-hud glass-panel">
      <div className="hud-block">
        <p className="hud-eyebrow">Current Surface</p>
        <div className="hud-primary">{active.label}</div>
        <div className="hud-support">
          <StatusDot tone={hasSession ? "green" : "amber"} label={hasSession ? "Session armed" : "Session empty"} />
        </div>
      </div>
      <div className="hud-metrics">
        <HealthBar label="Agents Online" value={hud ? Math.min(100, hud.agents_online) : 68} />
        <HealthBar label="Active Runs" value={hud ? Math.min(100, hud.runs_active * 12 || 4) : 64} />
        <div className="hud-inline-card">
          <p className="hud-inline-label">Operational Confidence</p>
          <ReliabilityPips score={hud && hud.alerts_open === 0 ? 4 : 3} />
        </div>
      </div>
      <div className="hud-actions">
        <div className="hud-clock">{clock}</div>
        <div className="hud-secondary">
          <StatusDot tone={hud && hud.alerts_open === 0 ? "green" : "amber"} label={hud ? `${hud.alerts_open} alerts` : "No live HUD"} />
        </div>
        <button type="button" className="control-button" onClick={onOpenSession}>
          Operator Session
        </button>
      </div>
    </header>
  );
}
