# Requirements: AI-Enterprise

**Defined:** 2026-03-08
**Core Value:** Duplicate the real operational system into a clean architecture without losing live program coverage, agent hierarchy fidelity, or operator control.

## v1 Requirements

### Audit And Mapping

- [x] **AUD-01**: Source codebase map exists for the brownfield system and captures stack, integrations, architecture, structure, conventions, testing, and concerns
- [x] **AUD-02**: Duplication scope distinguishes first-party source code from vendor/generated/duplicate trees
- [x] **AUD-03**: Programs, applications, agents, datastores, and external connections are traceable back to the source system

### Duplication Backbone

- [x] **DUP-01**: AI-Enterprise duplicates first-party programs and agents from the source repo without copying nested VCS metadata or build artifacts
- [x] **DUP-02**: Registry IDs, application IDs, master ownership, and canonical agent file contracts remain traceable during duplication
- [x] **DUP-03**: The rebuild preserves backend operational behavior needed by current live programs

### Agents And Orchestration

- [x] **AGT-01**: AI-Enterprise includes complete canonical packets for IAn and Engineer
- [x] **AGT-02**: Program Masters and Specialists preserve current role boundaries and routing responsibilities
- [x] **AGT-03**: IAn can route work to Program Masters, Specialists, and Engineer with observable run state

### API And Backend

- [x] **API-01**: The new backend exposes normalized control-plane endpoints for agents, programs, orchestration, reporting, and secrets
- [x] **API-02**: Existing live API and route contracts from the source system have a compatibility mapping or an intentional replacement plan
- [x] **API-03**: Runtime persistence and registry data can be migrated or reconstructed without losing source-system truth

### Security And Secrets

- [x] **SEC-01**: Secrets are managed server-side and never stored in browser `localStorage` or shipped in the frontend bundle
- [x] **SEC-02**: Write and settings endpoints use consistent authorization rules
- [x] **SEC-03**: Connection status can be tested and surfaced without exposing secret values

### Frontend

- [x] **UI-01**: The new mission-control frontend implements `/`, `/programs`, `/orchestration`, `/agents/configs`, `/report`, `/secrets`, and `/settings`
- [x] **UI-02**: The frontend follows the defined AI-Enterprise design system and component architecture
- [x] **UI-03**: Mock data is removed only after live backend wiring is complete

### Validation And Cutover

- [x] **VAL-01**: All P0 external connections have explicit validation status before live cutover
- [x] **VAL-02**: End-to-end IAn -> Program Master -> Specialist -> Engineer routing is demonstrated in the duplicated system
- [x] **VAL-03**: Build, contract, and security verification pass before AI-Enterprise is treated as live

### Operational Closure

- [x] **ORG-01**: AI-Enterprise reflects the target operating model with `IAn Agency` governance and top-level programs organized for operator clarity
- [x] **ORG-02**: Lavprishjemmeside explicitly models `CMS` and `client-sites`, with `lavprishjemmeside.dk` and `ljdesignstudio.dk` carried as governed client-site surfaces
- [x] **MIG-01**: Missing operational source context, including canonical Samlino subprojects, is either duplicated into the clean target or explicitly archived with traceable registry coverage
- [x] **MIG-02**: Supabase is removed from live AI-Enterprise runtime and registry paths, or fully demoted out of the operational surface with a locked replacement path
- [x] **SEC-04**: Remote deployment surfaces do not embed secret values in web-server or Passenger config
- [x] **VAL-04**: Post-reorganization verification proves remote cPanel surfaces, datastores, and portfolio registry state remain healthy

### Infrastructure Governance

- [x] **INF-01**: Git is the canonical source of truth for AI-Enterprise and managed first-party program code; cPanel and SSH hosts are deploy targets, not authoring truth
- [x] **INF-02**: The infrastructure model supports either GitHub-hosted or self-hosted Git remotes, including a Tailscale-reachable server, without changing local development workflow
- [x] **INF-03**: Repo topology is simple and top-level: one repo for AI-Enterprise plus separate repos only for independently deployed live surfaces
- [x] **INF-04**: Placeholder apps, archive context, and non-independent modules do not get their own repos by default
- [x] **INF-05**: The filesystem and repository hierarchy stay shallow and operator-readable at the top level
- [x] **VAL-05**: The chosen infrastructure model includes explicit validation for Git remote health, SSH access, deploy rollback, and source-to-live traceability

### Autonomy Infrastructure

- [x] **AUT-01**: AI-Enterprise can provision and bootstrap missing governed Git remotes without requiring a human to create the remote repository first
- [x] **AUT-02**: IAn and Engineer can execute scheduled or event-driven work on an always-on autonomy host rather than depending on an interactive laptop session
- [x] **AUT-03**: Autonomous write operations use non-human service credentials and server-side secret loading rather than personal-account browser or terminal state
- [x] **AUT-04**: Autonomous actions are gated by a kill switch, scoped approval policy, and durable audit trail
- [x] **AUT-05**: Repo provisioning, deploy provenance, and topology manifests stay synchronized automatically when new governed surfaces are created
- [x] **VAL-06**: The autonomy path is validated end-to-end, including remote provisioning, authenticated execution, and rollback-safe failure handling

## v2 Requirements

### Expansion

- **EXP-01**: Add new portfolio programs beyond the current source baseline
- **EXP-02**: Introduce operator account/RBAC workflows beyond the current single-operator model

## Out of Scope

| Feature | Reason |
|---------|--------|
| New greenfield portfolio products | This effort is focused on duplicating and hardening the existing system |
| Vendor/plugin source duplication as first-party code | High noise, low value, and poor maintainability |
| Browser-side storage of operational secrets | Explicitly rejected by the clean-slate security model |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| AUD-01 | Phase 1 | Complete |
| AUD-02 | Phase 1 | Complete |
| AUD-03 | Phase 1 | Complete |
| DUP-01 | Phase 2 | Complete |
| DUP-02 | Phase 2 | Complete |
| DUP-03 | Phase 3 | Complete |
| AGT-01 | Phase 3 | Complete |
| AGT-02 | Phase 3 | Complete |
| AGT-03 | Phase 5 | Complete |
| API-01 | Phase 5 | Complete |
| API-02 | Phase 2 | Complete |
| API-03 | Phase 2 | Complete |
| SEC-01 | Phase 4 | Complete |
| SEC-02 | Phase 4 | Complete |
| SEC-03 | Phase 4 | Complete |
| UI-01 | Phase 6 | Complete |
| UI-02 | Phase 6 | Complete |
| UI-03 | Phase 7 | Complete |
| VAL-01 | Phase 4 | Complete |
| VAL-02 | Phase 7 | Complete |
| VAL-03 | Phase 7 | Complete |
| ORG-01 | Phase 8 | Complete |
| ORG-02 | Phase 8 | Complete |
| MIG-01 | Phase 8 | Complete |
| MIG-02 | Phase 8 | Complete |
| SEC-04 | Phase 8 | Complete |
| VAL-04 | Phase 8 | Complete |
| INF-01 | Phase 9 | Complete |
| INF-02 | Phase 9 | Complete |
| INF-03 | Phase 9 | Complete |
| INF-04 | Phase 9 | Complete |
| INF-05 | Phase 9 | Complete |
| VAL-05 | Phase 9 | Complete |
| AUT-01 | Phase 10 | Complete |
| AUT-02 | Phase 10 | Complete |
| AUT-03 | Phase 10 | Complete |
| AUT-04 | Phase 10 | Complete |
| AUT-05 | Phase 10 | Complete |
| VAL-06 | Phase 10 | Complete |

**Coverage:**
- v1 requirements: 39 total
- Mapped to phases: 39
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-08*
*Last updated: 2026-03-08 after completing autonomy infrastructure requirements for Phase 10*
