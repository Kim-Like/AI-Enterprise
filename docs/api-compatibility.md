# API Compatibility Notes

## Scope

This document tracks source-to-target compatibility-critical contracts during the clean AI-Enterprise duplication.

## Canonical Program IDs

- `ian-control-plane`
- `artisan-reporting`
- `artisan-wordpress`
- `artisan-email-marketing`
- `lavprishjemmeside-cms`
- `samlino-seo-agent-playground`
- `baltzer-tcg-index`
- `baltzer-reporting`
- `baltzer-shopify`
- `personal-assistant-suite`

## Source Route Mapping

| Source Route | Target Status | Notes |
|--------------|---------------|-------|
| `/health` | implemented in Phase 2 | clean runtime health check preserved |
| `/api/meta/runtime` | implemented in Phase 2 | runtime diagnostics preserved |
| `/api/datastores/verify` | implemented in Phase 4 | route preserved and hardened behind write authorization |
| `/api/control-ui/secrets/status` | implemented in Phase 4 | normalized secrets-status surface added early because Phase 4 requires it |
| `/api/control-ui/secrets/test/{key_name}` | implemented in Phase 4 | redacted targeted connection test surface added early |
| `/api/applications` | implemented in Phase 5 | list/detail/rescan routes backed by duplicated application registry and specialist sync |
| `/api/control-ui/*` | implemented in Phase 5 | agents, programs, reporting, secrets, orchestration, and compatibility aliases are now served by the clean backend |
| `/api/chat/*` | deferred to later phase | not required for backend foundation |
| `/api/orchestration/*` | implemented in Phase 5 | source-compatible flow/run routes preserved with hardened write authorization |

## Phase 5 Compatibility Notes

- `/api/control-ui/floor`, `/api/control-ui/agents/configs*`, and `/api/control-ui/report/state` remain as explicit aliases over the normalized read service.
- Normalized orchestration routes live at `/api/control-ui/orchestration/overview`, `/api/control-ui/orchestration/runs`, `/api/control-ui/orchestration/runs/{id}`, and `/api/control-ui/orchestration/trigger`.
- Source-compatible orchestration writes remain available under `/api/orchestration/*`, but the clean target intentionally hardens them behind Phase 4 write authorization instead of leaving them opportunistically open.

## Catalog Compatibility

- Source application IDs are preserved in `api/config/application_catalog.json`.
- Source task template IDs are preserved in `api/config/task_catalog.json`.
- Source ownership rules are preserved in `api/agent/ownership_rules.py`.

## Clean-Build Rule

Compatibility in Phase 2 means preserving canonical IDs, registry sync, and foundational route viability without copying the legacy frontend or generated static assets.
