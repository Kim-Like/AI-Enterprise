import { NavLink } from "react-router-dom";
import type { NavItem } from "../../App";

type NavRailProps = {
  items: NavItem[];
};

export function NavRail({ items }: NavRailProps) {
  return (
    <nav className="nav-rail glass-panel" aria-label="Mission control navigation">
      <div className="nav-brand">
        <span className="nav-brand-mark">AE</span>
        <div>
          <div className="nav-brand-title">AI-Enterprise</div>
          <div className="nav-brand-subtitle">Mission Control</div>
        </div>
      </div>
      <div className="nav-links">
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) => `nav-link ${isActive ? "is-active" : ""}`}
          >
            <span className="nav-link-eyebrow">{item.eyebrow}</span>
            <span className="nav-link-label">{item.label}</span>
          </NavLink>
        ))}
      </div>
      <div className="nav-footer">
        <p className="nav-footer-title">Shift Mode</p>
        <p className="nav-footer-copy">Single-operator, in-memory control session, no browser-persistent secrets.</p>
      </div>
    </nav>
  );
}
