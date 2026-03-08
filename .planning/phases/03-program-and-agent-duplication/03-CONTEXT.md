# Phase 3: Program And Agent Duplication - Context

**Gathered:** 2026-03-08
**Status:** Ready for planning
**Source:** Phase 1 traceability + source agent/program tree + clean backend target

<domain>
## Phase Boundary

Duplicate the source agent hierarchy and first-party program payloads into `/Users/IAn/Agent/AI-Enterprise` without dragging nested repos, caches, build artifacts, vendor trees, or orphan incubators into the clean project. This phase establishes the target `/agents` and `/programs` trees so later phases can wire secrets, orchestration, APIs, and frontend behavior against real duplicated assets.

</domain>

<decisions>
## Implementation Decisions

### Target hierarchy
- The clean target must use `/Users/IAn/Agent/AI-Enterprise/agents` and `/Users/IAn/Agent/AI-Enterprise/programs`.
- Copy source `father/` into `AI-Enterprise/agents/IAn/`.
- Copy source `engineer/` into `AI-Enterprise/agents/Engineer/`.
- Normalize program masters and specialists into program-scoped agent directories under `AI-Enterprise/agents/<domain>/...` rather than copying the source `masters/` folder shape verbatim.

### Canonical agent scope
- Preserve the core hierarchy frozen in `01-SOURCE-TRACEABILITY.md`: IAn, Engineer, and the program masters for `ian`, `artisan`, `lavprishjemmeside`, `samlino`, `baltzer`, and `personal-assistant`.
- Preserve current specialist task packets under their owning program master.
- Do not carry forward `masters/Orchestration` as an active clean-build hierarchy node.
- Do not treat `programs/samlino/seo-agent-playground/ian` as part of the core hierarchy.

### Program payload scope
- Duplicate canonical first-party program payloads into `AI-Enterprise/programs`.
- Keep placeholder/pending programs as lightweight duplicated placeholders when that is the actual source state.
- Preserve source-relative structure for canonical programs while excluding nested repos, dependency caches, local virtual environments, generated bundles, and orphan incubators.

### Exclusions and hygiene
- Exclude `.git`, `node_modules`, `venv`, `.venv`, `__pycache__`, `.pytest_cache`, `dist`, `build`, `.next`, `vendor`, WordPress `uploads`, and similar generated/runtime trees.
- Exclude `programs/samlino/seo-agent-playground/AI-visibility`, `AI-Visibility copy`, `samlino-mind-map`, and `seo-auditor` from canonical duplication.
- Exclude nested duplicate WordPress copy at `programs/artisan/reporting.theartisan.dk/the-artisan-wp`.
- Clean caches already created in the target root so `AI-Enterprise` remains a clean project, not a working-directory dump.

### Traceability
- Preserve source ownership and routing intent through manifests or docs checked into the target root.
- Record what was intentionally excluded so later phases do not mistake omissions for missing work.

### Claude's Discretion
- Exact manifest/document names in the target root
- Whether copied placeholders are represented by empty folders plus README/notes or by copied scaffolds
- The exact pytest layout for filesystem duplication checks

</decisions>

<specifics>
## Specific Ideas

- Add `AI-Enterprise/.gitignore` now to keep the new project clean.
- Add `AI-Enterprise/docs/agent-hierarchy.md` to map source hierarchy to target hierarchy.
- Add `AI-Enterprise/docs/program-payloads.md` to record copied programs and explicit exclusions.
- Add pytest checks that verify canonical files for IAn/Engineer/program masters and key copied program directories.

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `father/`, `engineer/`, and the complete canonical master directories under `masters/*`
- Specialist packets under `masters/*/tasks/*` and `engineer/tasks/*`
- Program payload roots under `programs/artisan`, `programs/baltzer`, `programs/samlino`, and `programs/personal-assistant`
- `01-SOURCE-TRACEABILITY.md` as the frozen source inventory

### Established Patterns
- Core agents and program masters all have full 8-file canonical packets except `masters/Orchestration`
- Specialists generally preserve source task packet shape rather than full 8-file packets
- Program payloads include large amounts of duplicate or generated material that must be excluded deliberately

### Integration Points
- `AI-Enterprise/api/agent/identity_loader.py` will eventually consume copied agent directories
- Later backend and orchestration phases need the duplicated `programs/` payload tree in place
- The copied payloads must remain consistent with the canonical IDs seeded in Phase 2 registry sync

</code_context>

<deferred>
## Deferred Ideas

- Secrets wiring and connection validation belong to Phase 4
- Control-plane API normalization belongs to Phase 5
- Frontend rebuild belongs to Phase 6
- Live cutover and end-to-end validation belong to Phase 7

</deferred>

---

*Phase: 03-program-and-agent-duplication*
*Context gathered: 2026-03-08*
