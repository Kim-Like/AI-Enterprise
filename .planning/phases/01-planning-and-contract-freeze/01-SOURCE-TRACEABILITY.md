# Phase 1: Source Traceability Matrix

**Frozen:** 2026-03-08
**Source root:** `/Users/IAn/Agent/IAn`
**Target root (locked for implementation phases):** `/Users/IAn/Agent/AI-Enterprise`

## Purpose

This file freezes the source-system entities AI-Enterprise is duplicating from. It exists to satisfy `AUD-03` with concrete traceability for programs, applications, agents, datastores, and external connections.

## Programs

| Program ID | Source Path | Owner | Status | Duplication Notes |
|------------|-------------|-------|--------|-------------------|
| `ian-control-plane` | `/Users/IAn/Agent/IAn` | `father` | LIVE | Source control plane and brownfield contract baseline |
| `artisan-reporting` | `/Users/IAn/Agent/IAn/programs/artisan/reporting.theartisan.dk` | `artisan-master` | LIVE | Duplicate as first-party program payload |
| `artisan-wordpress` | `/Users/IAn/Agent/IAn/programs/artisan/the-artisan-wp` | `artisan-master` | LIVE | Duplicate first-party payload, exclude vendor/plugin internals as source-of-truth |
| `artisan-email-marketing` | `/Users/IAn/Agent/IAn/programs/artisan/e-mail-marketing` | `artisan-master` | PENDING | Keep as planned placeholder |
| `lavprishjemmeside-cms` | SSH-first source recorded in registry | `lavprishjemmeside-master` | PARTIAL | Duplicate from audited local metadata first; connection validation remains separate |
| `samlino-seo-agent-playground` | `/Users/IAn/Agent/IAn/programs/samlino/seo-agent-playground` | `samlino-master` | PARTIAL | Includes runtime modules directly loaded by source backend |
| `baltzer-tcg-index` | `/Users/IAn/Agent/IAn/programs/baltzer/TCG-index` | `baltzer-master` | PARTIAL | Duplicate first-party app code, not local build failures or secrets debt |
| `baltzer-reporting` | `/Users/IAn/Agent/IAn/programs/baltzer/reporting.baltzergames.dk` | `baltzer-master` | PARTIAL | Duplicate payload and reporting contract |
| `baltzer-shopify` | `/Users/IAn/Agent/IAn/programs/baltzer/shopify` | `baltzer-master` | PARTIAL | Duplicate registry truth even where local payload is sparse |
| `personal-assistant-suite` | `/Users/IAn/Agent/IAn/programs/personal-assistant` | `personal-assistant-master` | PENDING | Duplicate as placeholder program set |

## Applications

### Canonical applications from registry
- `ian-mission-control`
- `artisan-reporting-app`
- `artisan-wordpress-site`
- `artisan-b2b-dashboard-orders`
- `artisan-email-marketing`
- `lavprishjemmeside-ai-cms`
- `lavprishjemmeside-seo-dashboard`
- `lavprishjemmeside-ads-dashboard`
- `lavprishjemmeside-client-subscription-overview`
- `samlino-seo-agent-playground-app`
- `samlino-seo-schema-runtime`
- `samlino-seo-audit-runtime`
- `samlino-prototyper-runtime`
- `baltzer-tcg-index-app`
- `baltzer-reporting-app`
- `baltzer-shopify-core`
- `baltzer-social-media-management`
- `baltzer-event-management-platform`
- `baltzer-employee-schedule-salary-api`
- `personal-assistant-calendar-management`
- `personal-assistant-email-management`
- `personal-assistant-fitness-dashboard`
- `personal-assistant-social-media-management`
- `personal-assistant-task-manager`

### Orphan or duplicate candidates to track but not treat as canonical
- `programs/samlino/seo-agent-playground/AI-visibility` - PARTIAL incubator
- `programs/samlino/seo-agent-playground/samlino-mind-map` - PARTIAL incubator
- `programs/samlino/seo-agent-playground/seo-auditor/audit-server` - PARTIAL runtime service
- `programs/samlino/seo-agent-playground/AI-visibility/AI-Visibility copy` - DEAD duplicate

## Agents

**Filesystem totals frozen for duplication planning:**
- 44 first-party agent directories
- Roles: `FATHER 1`, `LEAD 1`, `MASTER 7`, `SPECIALIST 34`, `UNKNOWN 1`
- Functional status: `REAL 42`, `PARTIAL 2`, `DUMMY 0`

**Core hierarchy to preserve:**
- `father/`
- `engineer/`
- `masters/ian-master/`
- `masters/artisan-master/`
- `masters/lavprishjemmeside-master/`
- `masters/samlino-master/`
- `masters/baltzer-master/`
- `masters/personal-assistant-master/`

**Special handling:**
- `masters/Orchestration` is historical/partial and should not be the clean-build reference master
- `programs/samlino/seo-agent-playground/ian` is legacy local agent context, not a core hierarchy node

## Datastores

| Datastore ID | Program | Status | Duplication Handling |
|--------------|---------|--------|----------------------|
| `father-db` | `ian-control-plane` | verified | Preserve schema and compatibility inputs |
| `artisan-reporting-local-state` | `artisan-reporting` | configured | Duplicate env contract and validation rules |
| `artisan-wordpress-cpanel-mysql` | `artisan-wordpress` | configured | Duplicate env contract and validation rules |
| `lavprishjemmeside-cpanel-mysql` | `lavprishjemmeside-cms` | missing_env | Preserve as missing/partial until validated |
| `samlino-module-storage` | `samlino-seo-agent-playground` | missing_path | Preserve as missing/partial until validated |
| `baltzer-tcg-supabase` | `baltzer-tcg-index` | missing_env | Preserve as missing/partial until validated |
| `baltzer-reporting-local-state` | `baltzer-reporting` | verified | Duplicate local-state contract |
| `baltzer-shopify-cloud` | `baltzer-shopify` | missing_env | Preserve as missing/partial until validated |
| `personal-assistant-local` | `personal-assistant-suite` | planned | Preserve as planned placeholder |

## External Connections

### GitHub or repo references
- `git@github.com:kimjeppesen01/reporting.theartisan.dk.git`
- `https://github.com/kimjeppesen01/the-artisan.git`
- `https://github.com/kimjeppesen01/card-pulse.git`
- `https://github.com/SamlinoDK/seo-agent-playground.git`
- `https://github.com/SamlinoDK/ai-clarity.git`
- `https://github.com/SamlinoDK/samlino-mind-map.git`

### SSH and remote ops
- cPanel SSH contract via `CPANEL_SSH_HOST`, `CPANEL_SSH_USER`, `CPANEL_SSH_PORT`, and SSH key path env vars
- GitHub SSH access currently missing in the audited workstation

### Auth and provider contracts
- Claude CLI OAuth session is current-state live evidence
- Control-plane write auth currently uses `X-Admin-Key` and autonomy header
- Billy, Supabase, Shopify, and cPanel API/MySQL env contracts are frozen as duplication inputs

## Exclusions Frozen For Duplication

- `node_modules/`, `venv/`, `.venv/`, build artifacts, logs, backups, nested `.git`, duplicate incubators, and vendor/plugin dependency trees
- `backend/static/ui/` is retained as generated-output evidence only, not source of truth

## Traceability Rule

Every implementation phase after Phase 1 must be able to point back to one or more rows or sections in this file when duplicating a source program, agent, datastore, or external connection contract.

---

*Phase: 01-planning-and-contract-freeze*
*Traceability frozen: 2026-03-08*
