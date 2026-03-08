# AI-Enterprise

## What This Is

AI-Enterprise is a clean-slate rebuild project for the existing IAn control plane and its managed program portfolio. It duplicates the live first-party programs, agents, orchestration behavior, and operator-facing functionality from `/Users/IAn/Agent/IAn` into a new, safer, more maintainable target architecture without carrying forward browser-side secrets, route drift, or mixed source-of-truth sprawl.

## Core Value

Duplicate the real operational system into a clean architecture without losing live program coverage, agent hierarchy fidelity, or operator control.

## Requirements

### Validated

- [x] Current source system already provides agent orchestration, portfolio registry, and a control-plane UI in `/Users/IAn/Agent/IAn`
- [x] The clean rebuild must preserve live first-party program and agent functionality rather than inventing a new product

### Active

- [ ] Build a GSD-native planning and execution path for AI-Enterprise using the mapped source codebase as truth
- [ ] Duplicate core control-plane backend, agents, programs, and operational contracts into a clean target structure
- [ ] Rebuild the frontend and secrets/auth posture while preserving required operator workflows

### Out of Scope

- Adding new portfolio products beyond the source system baseline — this project is duplication and hardening first
- Copying vendor trees, generated assets, nested VCS metadata, or duplicate incubator apps as first-party code — these create noise and drift
- Preserving browser-side secret storage or weak route protections — the rebuild exists partly to remove those patterns

## Context

The source codebase is the brownfield repo at `/Users/IAn/Agent/IAn`. Its mapped baseline now lives in `.planning/codebase/STACK.md`, `.planning/codebase/INTEGRATIONS.md`, `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/STRUCTURE.md`, `.planning/codebase/CONVENTIONS.md`, `.planning/codebase/TESTING.md`, and `.planning/codebase/CONCERNS.md`. The master project PRD is `/Users/IAn/Downloads/PLAN.md`, which defines the clean-slate AI-Enterprise target, duplication boundaries, design system, API normalization, secrets model, and execution checklist.

## Constraints

- **Source boundary**: `/Users/IAn/Agent/IAn` is the codebase being duplicated — it is the source of truth for programs, agents, contracts, and operational behavior.
- **Workflow**: GSD planning must be valid and executable — roadmap, requirements, context, research, validation, and phase plans must all line up.
- **Security**: No secret values may be copied into planning docs, and the rebuild must remove browser-side secret storage and weak write auth.
- **Migration scope**: Vendor/generated assets, logs, backups, and duplicate incubators are excluded from first-party duplication unless explicitly documented as risks.
- **Continuity**: Planning should support a long uninterrupted execution session with minimal follow-up discovery.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use `.planning/codebase/*` as the canonical source overview | The brownfield repo needed a stable codebase map before phase planning | ✓ Good |
| Treat `/Users/IAn/Downloads/PLAN.md` as the AI-Enterprise master PRD | It already contains the clean-slate target architecture and duplication intent | ✓ Good |
| Start with a duplication-first roadmap before implementation | The repo lacked a valid GSD roadmap, so `gsd-plan-phase` could not run safely | ✓ Good |
| Exclude vendor/generated/duplicate trees from first-party duplication | This keeps scope aligned with real maintainable functionality | ✓ Good |
| Create AI-Enterprise as `/Users/IAn/Agent/AI-Enterprise` | A sibling target root keeps source and duplicate clearly separated during execution | ✓ Good |

---
*Last updated: 2026-03-08 after initializing AI-Enterprise GSD planning from codebase map and master PRD*
