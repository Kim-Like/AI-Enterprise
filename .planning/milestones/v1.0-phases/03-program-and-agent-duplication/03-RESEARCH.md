# Phase 3: Program And Agent Duplication - Research

**Researched:** 2026-03-08
**Domain:** Filesystem duplication of canonical agent packets and first-party program payloads
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- The clean target must use `/Users/IAn/Agent/AI-Enterprise/agents` and `/Users/IAn/Agent/AI-Enterprise/programs`.
- Copy source `father/` into `AI-Enterprise/agents/IAn/`.
- Copy source `engineer/` into `AI-Enterprise/agents/Engineer/`.
- Normalize program masters and specialists into program-scoped agent directories under `AI-Enterprise/agents/<domain>/...`.
- Preserve the core hierarchy frozen in `01-SOURCE-TRACEABILITY.md`.
- Do not carry forward `masters/Orchestration` as an active clean-build hierarchy node.
- Exclude `.git`, `node_modules`, `venv`, `.venv`, `__pycache__`, `.pytest_cache`, `dist`, `build`, `.next`, `vendor`, WordPress `uploads`, and similar generated/runtime trees.
- Exclude `AI-visibility`, `AI-Visibility copy`, `samlino-mind-map`, `seo-auditor`, and the nested duplicate `reporting.theartisan.dk/the-artisan-wp`.

### Claude's Discretion
- Exact manifest/document names in the target root
- Placeholder duplication representation
- Exact pytest layout for duplication checks

### Deferred Ideas (OUT OF SCOPE)
- Secrets wiring and connection validation
- Control-plane API normalization
- Frontend rebuild
- Live cutover

</user_constraints>

<research_summary>
## Summary

Phase 3 is a selective copy-and-normalize phase. The source codebase already contains the authoritative agent packets and program payload trees, but they are mixed with nested git repos, dependency caches, WordPress vendor/plugin internals, Python virtual environments, and incubator branches that do not belong in the clean duplicate. The correct approach is not “copy everything under `programs/` and `masters/`”; it is “copy only the canonical first-party payloads, with explicit exclusions and traceability.”

For agents, the clean target should normalize the hierarchy while preserving source content. `father` and `engineer` become top-level clean nodes, masters become domain-scoped nodes, and specialists stay attached to their owning master. For programs, rsync-style filtered copy is the safest approach because the source trees are large and dirty, especially under Artisan WordPress and Samlino. Exclusions must be codified rather than applied ad hoc.

**Primary recommendation:** execute Phase 3 with deterministic filtered copy rules, create target manifests that document what was copied and what was excluded, and back the result with pytest checks so later phases inherit a clean, auditable asset tree.
</research_summary>

<standard_stack>
## Standard Stack

### Core
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| `rsync` | system | selective directory duplication | efficient filtered copy for large dirty trees |
| `pytest` | source current | duplication verification | already present in the clean target |
| Markdown manifests | n/a | duplication traceability | simplest durable record of copy rules and exclusions |

### Supporting
| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| `.gitignore` | n/a | target hygiene | use immediately once target asset trees exist |
| Python stdlib `pathlib` | stdlib | filesystem verification | use in tests for portable duplication checks |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| filtered `rsync` | Python copy scripts | slower to author and easier to get subtly wrong |
| normalized target hierarchy | mirror source `masters/` exactly | faster, but preserves legacy structure the clean build is trying to improve |
| explicit manifests | tribal knowledge in plans only | loses traceability during later phases |

</standard_stack>

<architecture_patterns>
## Architecture Patterns

### Pattern 1: Normalize While Preserving Content
**What:** keep the source markdown packet contents and program payload files, but place them into a cleaner target directory model.
**When to use:** for agents in particular, where the source `father/engineer/masters/*` layout is not the target shape.

### Pattern 2: Filtered Copy with Stable Exclusion Rules
**What:** copy directories using a fixed exclusion list for caches, nested repos, vendor trees, and orphan incubators.
**When to use:** for all program payload duplication in this phase.

### Pattern 3: Manifest-Backed Duplication
**What:** create checked-in docs that describe source-to-target mappings and intentional exclusions.
**When to use:** whenever copy rules would otherwise be hard to reconstruct later.

### Anti-Patterns to Avoid
- **Bulk copy without exclusions:** guarantees dirty target trees and makes later work slower.
- **Rewriting agent packet content during duplication:** risks losing source truth and blurring phases.
- **Carrying partial/historical nodes as active hierarchy:** especially `masters/Orchestration` and Samlino local-agent remnants.

</architecture_patterns>

<dont_hand_roll>
## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| large-tree copy logic | custom recursive copier | `rsync` with explicit excludes | handles incremental dirty trees and is easier to audit |
| duplication verification | manual spot checks | pytest filesystem assertions | stable and repeatable |
| hierarchy memory | mental mapping | checked-in `agent-hierarchy.md` | later phases need durable source-to-target mapping |

**Key insight:** the risk in Phase 3 is not copy difficulty, it is copy contamination. The solution is explicit selection and verification, not more custom code than necessary.
</dont_hand_roll>

<common_pitfalls>
## Common Pitfalls

### Pitfall 1: Copying nested repos and caches into the target
**What goes wrong:** the clean project inherits `.git`, `node_modules`, `venv`, build directories, and WordPress uploads/vendor trees.
**Why it happens:** bulk copy at the top-level program directory without exclusions.
**How to avoid:** use a shared exclusion list and test for absence of those paths after copy.
**Warning signs:** target disk usage grows unexpectedly and `find` shows nested `.git` or `node_modules`.

### Pitfall 2: Preserving legacy hierarchy shape instead of the target model
**What goes wrong:** the target ends up with `masters/` plus duplicated top-level agents, which undermines the clean structure.
**Why it happens:** source paths are copied literally.
**How to avoid:** map source roles to target `agents/IAn`, `agents/Engineer`, and domain-scoped agent folders.
**Warning signs:** later phases need compatibility shims just to find agent packets.

### Pitfall 3: Copying orphan incubators as if they were canonical programs
**What goes wrong:** AI-Enterprise inherits duplicate or experimental Samlino surfaces that the Phase 1 traceability matrix explicitly excluded.
**Why it happens:** Samlino’s source tree contains multiple adjacent incubators and nested copies.
**How to avoid:** treat the Phase 1 traceability matrix as the copy contract and exclude the known orphan set.
**Warning signs:** `AI-Enterprise/programs/samlino/...` contains `AI-visibility`, `AI-Visibility copy`, or `samlino-mind-map`.

</common_pitfalls>

<open_questions>
## Open Questions

1. **Should WordPress plugin directories be copied at all?**
   - What we know: the source tree is dominated by third-party plugin/vendor code and uploads.
   - What's unclear: whether any plugin subtree is truly first-party.
   - Recommendation: copy theme-level first-party payload and keep plugin/vendor trees excluded unless later evidence proves a custom plugin must be restored.

2. **Should placeholder programs be copied as scaffolds or represented in manifests only?**
   - What we know: personal-assistant and several Baltzer/Artisan placeholders already exist as light source scaffolds.
   - What's unclear: whether empty target placeholders would be enough.
   - Recommendation: copy the existing placeholder scaffolds because they are small and preserve source truth.

## Validation Architecture

Phase 3 validation should prove:

- `AI-Enterprise/agents` exists and contains IAn, Engineer, and all canonical program masters.
- the copied IAn and Engineer packets contain all 8 canonical files.
- domain-scoped specialist directories exist for the source task packets.
- `AI-Enterprise/programs` contains canonical first-party program roots.
- excluded directories are absent from the target: nested `.git`, `node_modules`, `venv`, `.venv`, `__pycache__`, `.pytest_cache`, `AI-Visibility copy`, `AI-visibility`, `samlino-mind-map`, `seo-auditor`, nested duplicate `the-artisan-wp` under reporting.

<sources>
## Sources

### Primary (HIGH confidence)
- `01-SOURCE-TRACEABILITY.md`
- source directories: `father/`, `engineer/`, `masters/*`, `engineer/tasks/*`
- source directories: `programs/artisan`, `programs/baltzer`, `programs/samlino`, `programs/personal-assistant`
- current clean target root `/Users/IAn/Agent/AI-Enterprise`

### Secondary (MEDIUM confidence)
- `.planning/codebase/STRUCTURE.md`
- `.planning/codebase/CONCERNS.md`

### Tertiary (LOW confidence - needs validation)
- none
</sources>

<metadata>
## Metadata

**Research scope:**
- Core technology: filesystem duplication and normalization
- Ecosystem: agent packets, program payloads, exclusion rules
- Patterns: filtered copy, normalized hierarchy, manifest-backed duplication
- Pitfalls: nested repos, WordPress/vendor sprawl, orphan incubators

**Confidence breakdown:**
- Copy strategy: HIGH
- Hierarchy mapping: HIGH
- Exclusion rules: HIGH
- Unknown first-party plugin edge cases: MEDIUM

**Research date:** 2026-03-08
**Valid until:** 2026-04-07
</metadata>

---

*Phase: 03-program-and-agent-duplication*
*Research completed: 2026-03-08*
*Ready for planning: yes*
