# Roadmap: AI-Enterprise

## Overview

AI-Enterprise starts from a mapped brownfield control plane and duplicates it into a clean-slate target. The journey is: freeze the source-system contract, duplicate backend and portfolio truth, rebuild agent hierarchy and orchestration safely, harden secrets and connections, rebuild the frontend, then validate and cut over live functionality.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [x] **Phase 1: Planning And Contract Freeze** - Lock the source-system baseline, duplication rules, and executable overnight plan set
- [x] **Phase 2: Backend And Registry Duplication** - Duplicate core backend, persistence, registry, and compatibility contracts into AI-Enterprise
- [x] **Phase 3: Program And Agent Duplication** - Duplicate first-party programs, canonical agent packets, and hierarchy ownership
- [x] **Phase 4: Security, Secrets, And Connection Validation** - Rebuild auth/secrets posture and validate external dependencies
- [x] **Phase 5: Orchestration And Control API Normalization** - Align runtime orchestration and control-plane endpoints with the clean-slate contract
- [x] **Phase 6: Mission Control Frontend Rebuild** - Rebuild the UI shell, routes, drawers, and design system
- [x] **Phase 7: Live Wiring, Validation, And Cutover** - Remove mocks, run end-to-end validation, and prepare live cutover
- [x] **Phase 8: Operational Portfolio Reorganization And Residual Migration Closure** - Reorganize the duplicated portfolio, close residual source gaps, remove legacy datastore drift, and harden remote deployment surfaces
- [x] **Phase 9: Infrastructure Topology, Git Source Of Truth, And Deployment Governance Simplification** - Define the canonical infrastructure model, Git topology, and deployment governance for operating AI-Enterprise without repo sprawl

## Phase Details

### Phase 1: Planning And Contract Freeze
**Goal**: Turn the AI-Enterprise master plan and source codebase map into a GSD-ready, execution-grade duplication program without changing source-system functionality.
**Depends on**: Nothing (first phase)
**Requirements**: [AUD-01, AUD-02, AUD-03]
**Success Criteria** (what must be TRUE):
  1. Source-system scope, exclusions, contracts, and duplication boundaries are documented and stable.
  2. GSD planning state exists and supports downstream uninterrupted execution.
  3. At least one verified executable plan exists for beginning duplication work.
**Plans**: 2 plans

Plans:
- [x] 01-01: Establish GSD scaffold from master PRD and codebase map
- [x] 01-02: Produce validated execution plans for duplication foundation work

### Phase 2: Backend And Registry Duplication
**Goal**: Duplicate backend runtime, persistence, registry metadata, and compatibility-critical IDs into AI-Enterprise without frontend rebuild work.
**Depends on**: Phase 1
**Requirements**: [DUP-01, DUP-02, API-02, API-03]
**Success Criteria** (what must be TRUE):
  1. AI-Enterprise has a duplicated backend/runtime skeleton with registry and DB foundations.
  2. Program/application/master ownership IDs from the source system remain traceable.
  3. No vendor/build/nested VCS noise is treated as first-party duplicated code.
**Plans**: TBD

Plans:
- [x] 02-01: Duplicate backend runtime and persistence foundation
- [x] 02-02: Duplicate registry and compatibility contracts

### Phase 3: Program And Agent Duplication
**Goal**: Duplicate first-party programs, canonical agent packets, and hierarchy ownership into the new project structure.
**Depends on**: Phase 2
**Requirements**: [DUP-03, AGT-01, AGT-02]
**Success Criteria** (what must be TRUE):
  1. IAn, Engineer, Program Masters, and active Specialists exist in AI-Enterprise with canonical files.
  2. First-party programs and applications are duplicated into the new target structure.
  3. The new hierarchy preserves current role ownership and routing intent.
**Plans**: TBD

Plans:
- [x] 03-01: Duplicate canonical agent hierarchy
- [x] 03-02: Duplicate first-party program payloads

### Phase 4: Security, Secrets, And Connection Validation
**Goal**: Replace weak auth and browser-side secret handling with a server-managed model and validated external connection inventory.
**Depends on**: Phase 3
**Requirements**: [SEC-01, SEC-02, SEC-03, VAL-01]
**Success Criteria** (what must be TRUE):
  1. Secrets are no longer stored in browser `localStorage` or shipped in frontend bundles.
  2. Write and settings endpoints follow a consistent authorization model.
  3. External integrations report live, partial, or missing status with testable evidence.
**Plans**: TBD

Plans:
- [x] 04-01: Rebuild auth and secrets handling
- [x] 04-02: Implement connection validation and secrets status surfaces

### Phase 5: Orchestration And Control API Normalization
**Goal**: Normalize orchestration and control-plane APIs while preserving required operator workflows and routing behavior.
**Depends on**: Phase 4
**Requirements**: [AGT-03, API-01]
**Success Criteria** (what must be TRUE):
  1. Clean-slate control-plane endpoints for agents, orchestration, programs, reporting, and secrets exist.
  2. Required source-system route and payload contracts are mapped or intentionally versioned.
  3. IAn routing and run-state visibility work in the duplicated backend.
**Plans**: TBD

Plans:
- [x] 05-01: Normalize control-plane APIs
- [x] 05-02: Rebuild orchestration surfaces and run-state contracts

### Phase 6: Mission Control Frontend Rebuild
**Goal**: Rebuild the operator UI from scratch against the clean backend using the AI-Enterprise design system.
**Depends on**: Phase 5
**Requirements**: [UI-01, UI-02]
**Success Criteria** (what must be TRUE):
  1. All required routes exist and use the planned mission-control design language.
  2. Drawers, HUD, reporting, secrets, and orchestration surfaces operate against the new APIs.
  3. The frontend preserves density and operational clarity without carrying forward old UI drift.
**Plans**: TBD

Plans:
- [x] 06-01: Build app shell and shared design system
- [x] 06-02: Implement route surfaces and live data wiring

### Phase 7: Live Wiring, Validation, And Cutover
**Goal**: Remove mocks, complete end-to-end validation, and prepare AI-Enterprise for live operational use.
**Depends on**: Phase 6
**Requirements**: [UI-03, VAL-02, VAL-03]
**Success Criteria** (what must be TRUE):
  1. Mock data is removed and live system state flows end-to-end.
  2. IAn -> Program Master -> Specialist -> Engineer execution is validated.
  3. Build, contract, and security checks pass for the duplicated system.
**Plans**: TBD

Plans:
- [x] 07-01: Remove mocks and complete end-to-end validation
- [x] 07-02: Prepare cutover and operational readiness

### Phase 8: Operational Portfolio Reorganization And Residual Migration Closure
**Goal**: Align AI-Enterprise to the target operating model by reorganizing the portfolio hierarchy, carrying forward missing operational context, removing residual Supabase dependencies, and hardening remote deployment/runtime surfaces discovered during verification.
**Depends on**: Phase 7
**Requirements**: [ORG-01, ORG-02, MIG-01, MIG-02, SEC-04, VAL-04]
**Success Criteria** (what must be TRUE):
  1. The AI-Enterprise filesystem and registry reflect the intended `IAn Agency -> Programs` operating model, including explicit Lavprishjemmeside `CMS` and `client-sites` structure.
  2. Missing Samlino operational context is either duplicated into the clean target or explicitly archived with traceable registry coverage.
  3. Supabase is removed from live AI-Enterprise runtime and registry paths, or downgraded out of the operational surface with an explicit replacement.
  4. Remote cPanel deployment surfaces no longer embed sensitive values in deployment config, and post-reorganization verification proves the live surfaces still work.
**Plans**: 2 plans

Plans:
- [x] 08-01: Reorganize portfolio hierarchy and carry over missing context
- [x] 08-02: Close residual datastore and remote deployment gaps

### Phase 9: Infrastructure Topology, Git Source Of Truth, And Deployment Governance Simplification
**Goal**: Lock the long-term infrastructure model for AI-Enterprise by deciding the source-of-truth system, Git hosting topology, deployment boundaries, and the simplest sustainable top-level repository and folder structure.
**Depends on**: Phase 8
**Requirements**: [INF-01, INF-02, INF-03, INF-04, INF-05, VAL-05]
**Success Criteria** (what must be TRUE):
  1. AI-Enterprise has a documented source-of-truth model that distinguishes Git from deploy targets and does not depend on GitHub specifically.
  2. The portfolio has a simple repo topology with separate repos only where live deploy boundaries justify them.
  3. A self-hosted or GitHub-backed operating model is compared explicitly, with Tailscale-hosted Git treated as a valid option if it satisfies validation and rollback requirements.
  4. The top-level folder and repo hierarchy is simple enough to govern locally without mixing live cPanel state into source control truth.
**Plans**: 2 plans

Plans:
- [x] 09-01: Lock source-of-truth policy and repo topology
- [x] 09-02: Add Git governance, validation, and deploy provenance scaffolding

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9 -> 10

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Planning And Contract Freeze | 2/2 | Complete   | 2026-03-08 |
| 2. Backend And Registry Duplication | 2/2 | Complete   | 2026-03-08 |
| 3. Program And Agent Duplication | 2/2 | Complete   | 2026-03-08 |
| 4. Security, Secrets, And Connection Validation | 2/2 | Complete   | 2026-03-08 |
| 5. Orchestration And Control API Normalization | 2/2 | Complete   | 2026-03-08 |
| 6. Mission Control Frontend Rebuild | 2/2 | Complete | 2026-03-08 |
| 7. Live Wiring, Validation, And Cutover | 2/2 | Complete | 2026-03-08 |
| 8. Operational Portfolio Reorganization And Residual Migration Closure | 2/2 | Complete | 2026-03-08 |
| 9. Infrastructure Topology, Git Source Of Truth, And Deployment Governance Simplification | 2/2 | Complete | 2026-03-08 |
| 10. Autonomy infrastructure and repo provisioning | 2/2 | Complete | 2026-03-08 |

### Phase 10: Autonomy infrastructure and repo provisioning

**Goal**: Remove human dependency from routine AI-Enterprise repo provisioning, execution triggering, and deployment governance by adding an always-on autonomy executor, non-human control identities, and audited safety rails.
**Requirements**: [AUT-01, AUT-02, AUT-03, AUT-04, AUT-05, VAL-06]
**Depends on:** Phase 9
**Success Criteria** (what must be TRUE):
  1. AI-Enterprise can provision and bootstrap missing governed Git remotes without requiring a human to manually create them first.
  2. IAn and Engineer have a documented, non-human execution path on an always-on host with schedule or event triggers.
  3. Autonomous write actions use service credentials and server-side secret storage, not operator-bound laptop state.
  4. Kill switch, approval boundaries, audit logs, and rollback rules exist for autonomous actions.
**Plans**: 2 plans

Plans:
- [x] 10-01: Add topology-driven autonomy provisioning and policy guardrails
- [x] 10-02: Add always-on executor runtime, audit trail, and canonical autonomy validation
