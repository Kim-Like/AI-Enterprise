type StatusDotProps = {
  tone: "amber" | "green" | "blue" | "red" | "dim";
  label?: string;
};

export function StatusDot({ tone, label }: StatusDotProps) {
  return (
    <span className="status-pill">
      <span className={`status-dot status-${tone}`} aria-hidden="true" />
      {label ? <span>{label}</span> : null}
    </span>
  );
}
