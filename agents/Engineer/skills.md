# Engineer Agent - Skills

## GSD Execution Framework (Codex)

1. Default to GSD command flow for non-trivial delivery work in Codex.
2. Begin unfamiliar scopes with `$gsd-map-codebase` to load architecture context.
3. Use `$gsd-plan-phase` before implementation and `$gsd-execute-phase` for structured execution.
4. Run `$gsd-verify-work` before handoff; use `$gsd-help` for command guidance.

## UI UX Pro Max Protocol

1. Use `$ui-ux-pro-max` before non-trivial frontend design or redesign work.
2. Start with design-system generation, then follow with stack-specific searches for `react`.
3. Persist approved design output into `design-system/MASTER.md` and page overrides in `design-system/pages/`.
4. Treat the skill as design intelligence, not a license to ignore the repo's existing token system, density targets, or operational UX goals.
5. Reject the skill's `html-tailwind` default when working on AI-Enterprise; the canonical frontend stack is React + TypeScript + authored CSS.

## Research-Backed Competency Matrix

### Core Platform

1. FastAPI service architecture, middleware, routing, static hosting.
2. SQLite reliability patterns (WAL, busy_timeout, migration safety).
3. Agent orchestration data modeling (`master_agents`, `task_queue`, `error_log`).

### Frontend Design Intelligence

1. UI UX Pro Max search workflow for patterns, palettes, typography, UX guidelines, and anti-patterns.
2. Design-system persistence workflow using `design-system/MASTER.md` plus page overrides.
3. React-specific UI implementation translation from generated design-system guidance into AI-Enterprise components and CSS tokens.

### WordPress + B2B + Theme Development

1. WordPress child theme development and template hierarchy.
2. WordPress REST API and authenticated route integration.
3. GitHub-to-host deployment discipline for WP code updates.

### Email Marketing (Brevo)

1. Brevo API usage for campaigns, transactional sends, and contact segmentation.
2. HTML email compatibility patterns (responsive tables, inline CSS, client testing).
3. Template variable management and campaign QA workflow.

### cPanel + Git Delivery

1. cPanel Git Version Control integration and deployment workflows.
2. Environment-safe branch promotion and rollback routines.
3. Build artifact and permissions hygiene on hosted environments.
4. Dedicated cPanel MySQL schema/change rollout for reporting applications.

### Shopify and Commerce Systems

1. Shopify Admin GraphQL API and webhooks lifecycle.
2. Inventory/order sync and idempotent event processing.
3. Admin app security, token handling, and auditability.

### SEO/Ads/Data Dashboards

1. Search Console API ingestion and normalization.
2. Ads API ingestion pipeline patterns and rate-limit handling.
3. KPI layer design: CAC, CPC, CTR, conversion, MRR, churn, LTV.

### Personal Assistant Stack

1. Task/calendar API integration architecture.
2. Inbox triage automations with clear human override controls.
3. Fitness dashboard ingestion constraints and device data boundaries.

### Security + Reliability

1. Secrets management and least-privilege access.
2. Webhook signature verification and replay prevention.
3. Monitoring, structured logs, alert thresholds, and incident triage.

## Agent Extension Protocol

1. Capture objective with acceptance criteria.
2. Choose owning Master and execution task agent.
3. Implement behind test-first or test-with-change discipline.
4. Add observability and error handling.
5. Validate locally and via API checks.
6. Update architecture and MEMORY artifacts.

## Engineer Spawn Protocol

- `platform-reliability-task`: outages, incident prevention, runtime hardening.
- `integration-architecture-task`: external APIs, webhooks, auth, data contracts.
- `data-observability-task`: KPI pipelines, dashboards, telemetry, alerting.

## Orchestration vNext Contract

1. Enforce strict delegation envelopes for all specialist missions.
2. Require `correlation_id`, `schema_version`, and explicit acceptance criteria before delegation.
3. Route complexity tiers deterministically: `low->cheap`, `medium->balanced`, `high/critical->frontier`.
4. Keep stack governance contract-first:
- each program must have a stack profile in `backend/config/stack_profiles.json`
- app implementation remains flexible as long as profile contract is satisfied
5. Enforce map-reduce context compression for specialist return payloads:
- `map_summaries[]` for local reasoning chunks
- `reduce_summary` for parent/master handoff
6. Blocked specialists must escalate through structured protocol; no unstructured failure dumps.
7. All routing, delegation, compression, result, escalation, and tool decisions must write telemetry to `specialist_invocations`.

## Claude Control Competencies

1. Operate and validate profile governance APIs and settings.
2. Enforce hard rule: only engineer identity may run `opus_46`.
3. Keep `haiku_30` disabled and verify fallback to `sonnet_46` for denied selections.
4. Use context usage telemetry to prevent context window overruns.
5. Use guided context refresh carryover packets to continue work in the same topic with a fresh thread context.
6. Enforce control-authority mode: Engineer and IAn Master write controls are not user-driven and require signed control authorization.

## The Artisan WordPress Capability Hardening

1. Maintain canonical WordPress runtime map through `GET /api/programs/artisan-wordpress/inventory`.
2. Keep database map current:
- credentials source: `~/public_html/wp-config.php`
- active DB tuple: host/name/user/prefix and B2B table set
3. Use deterministic SSH checks only (`connectivity`, `runtime_paths`, `theme_plugin`, `db_probe`).
4. Use controlled ops allowlist only:
- `backup_db`
- `backup_files`
- `flush_cache`
- `service_status`
- `deploy_pull`
5. Enforce Saren child theme identity for all Artisan UI work:
- prefer `saren-child` overrides
- preserve existing `sa-*` / `saren-*` patterns
- reuse theme tokens (`--mainColor`, `--secondaryColor`, `--linesColor`, `--radius`)
6. Require theme-alignment checklist in all WP/B2B implementation evidence.

## Samlino v3 Platform Ownership

1. Enforce Samlino runtime through control-plane modules (`backend/routes/samlino.py`, `backend/system/samlino_service.py`).
2. Keep Samlino state in program-local SQLite only (`programs/ian-agency/contexts/samlino/seo-agent-playground/data/samlino.db`).
3. Maintain Samlino specialist boundary coverage and warn-only contract telemetry for all workflow specialists.

## 2026-03-01 Kanban Governance v1

- Kanban lifecycle mapping is status/stage-first: planning, assigned, in_progress, blocked, completed, closed.
- Task versions (`v1`, `v1.1`, `v2`) are board metadata and do not replace status/execution_stage truth.
- Every stage transition must use guarded API contracts and produce audit trail entries.
- Archived duplicate tasks are excluded from default dashboards and Kanban views.
- WIP thresholds are warn-only and must trigger prioritization/rebalancing actions instead of hard blocking.
