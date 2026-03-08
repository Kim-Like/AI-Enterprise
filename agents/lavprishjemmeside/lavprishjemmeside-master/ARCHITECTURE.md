# Lavprishjemmeside Master Architecture

Parent: `father`

## Owned Program ID

- `lavprishjemmeside-cms`

## Task Agents

- `lph-ai-cms-task`
- `lph-seo-dashboard-task`
- `lph-ads-dashboard-task`
- `lph-subscription-ops-task`

## Critical Constraint

Treat cPanel MySQL as app data source of truth. Do not migrate app transactional data into `father.db`.


## Warn-Only Governance
- Boundary planning and overlap detection are contract-driven using the shared orchestration policy module.
- Contract violations are warnings, not blockers; orchestration remains autonomous.
- Structured result/escalation packets are mandatory interface targets for specialists.
- Operational diagnostics are triaged by `correlation_id` in telemetry and queue records.

## Claude Runtime Policy

- Use model profiles through policy-aware controls (`/api/models/catalog`, thread-level model override).
- Masters are not permitted to run `opus_46`; denied requests fall back to `sonnet_46` with warnings.
- `haiku_30` is a visible legacy profile and remains disabled by policy.
- Use context usage status (`ok|warning|critical|over`) to decide when to trigger context refresh carryover.
