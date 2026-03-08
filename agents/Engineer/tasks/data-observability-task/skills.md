# Data and Observability Task - Skills

## Domain Competencies
1. Telemetry modeling for KPIs, reliability signals, and execution throughput.
2. Data freshness, anomaly detection, and dashboard trustworthiness controls.
3. Measurement design that maps directly to business objectives and SLA targets.

## Execution Standards
1. Use Claude CLI (OAuth runtime) when AI generation/planning is required; no API-key-only fallback paths in v1.
2. Keep Python typing Python 3.9-safe (`Optional[T]`), and preserve deterministic ownership (`master_id`, `program_id`).
3. Always include tests/verification evidence and update task memory with blockers, risks, and next handoff.

## Definition of Done
- Deliverable is reproducible with explicit verification evidence.
- Acceptance criteria are met and handoff path is unambiguous.
- MEMORY and queue/error state are updated for the next agent hop.
