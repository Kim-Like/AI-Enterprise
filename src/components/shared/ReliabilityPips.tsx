type ReliabilityPipsProps = {
  score: number;
  total?: number;
};

export function ReliabilityPips({ score, total = 5 }: ReliabilityPipsProps) {
  return (
    <div className="reliability-pips" aria-label={`Reliability ${score} of ${total}`}>
      {Array.from({ length: total }, (_, index) => (
        <span
          key={`${total}-${index}`}
          className={`reliability-pip ${index < score ? "is-active" : ""}`}
        />
      ))}
    </div>
  );
}
