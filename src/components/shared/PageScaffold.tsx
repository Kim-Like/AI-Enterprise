import type { ReactNode } from "react";

type PageScaffoldProps = {
  eyebrow: string;
  title: string;
  description: string;
  actions?: ReactNode;
  children: ReactNode;
};

export function PageScaffold({
  eyebrow,
  title,
  description,
  actions,
  children,
}: PageScaffoldProps) {
  return (
    <section className="page-shell">
      <header className="page-header glass-panel">
        <div>
          <p className="page-eyebrow">{eyebrow}</p>
          <h1>{title}</h1>
          <p className="page-description">{description}</p>
        </div>
        {actions ? <div className="page-actions">{actions}</div> : null}
      </header>
      <div className="page-content">{children}</div>
    </section>
  );
}
