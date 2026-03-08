type SessionRequiredProps = {
  title?: string;
  detail: string;
};

export function SessionRequired({ title = "Operator Session Required", detail }: SessionRequiredProps) {
  return (
    <div className="session-required glass-panel">
      <p className="session-required-eyebrow">{title}</p>
      <p className="session-required-copy">{detail}</p>
    </div>
  );
}
