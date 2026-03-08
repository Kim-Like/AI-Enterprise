type HealthBarProps = {
  label: string;
  value: number;
};

export function HealthBar({ label, value }: HealthBarProps) {
  const width = Math.max(4, Math.min(100, value));
  return (
    <div className="health-bar-block">
      <div className="health-bar-label">
        <span>{label}</span>
        <span>{width}%</span>
      </div>
      <div className="health-bar-track" aria-label={`${label} ${width}%`}>
        <div className="health-bar-fill" style={{ width: `${width}%` }} />
      </div>
    </div>
  );
}
