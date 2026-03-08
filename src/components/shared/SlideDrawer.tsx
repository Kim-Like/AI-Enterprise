import type { ReactNode } from "react";

type SlideDrawerProps = {
  open: boolean;
  title: string;
  subtitle?: string;
  onClose: () => void;
  children: ReactNode;
};

export function SlideDrawer({ open, title, subtitle, onClose, children }: SlideDrawerProps) {
  if (!open) {
    return null;
  }

  return (
    <>
      <button className="drawer-backdrop" onClick={onClose} aria-label="Close drawer" />
      <aside className="slide-drawer">
        <header className="drawer-header">
          <div>
            <p className="drawer-eyebrow">Detail Panel</p>
            <h2>{title}</h2>
            {subtitle ? <p className="drawer-subtitle">{subtitle}</p> : null}
          </div>
          <button type="button" className="drawer-close" onClick={onClose}>
            Close
          </button>
        </header>
        <div className="drawer-body">{children}</div>
      </aside>
    </>
  );
}
