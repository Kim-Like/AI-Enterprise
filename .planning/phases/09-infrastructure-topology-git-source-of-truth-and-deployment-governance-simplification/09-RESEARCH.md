---
phase: 9
slug: infrastructure-topology-git-source-of-truth-and-deployment-governance-simplification
created: 2026-03-08
status: complete
---

# Phase 9 Research

**Researched:** 2026-03-08
**Domain:** Infrastructure topology, Git source of truth, self-hosted versus GitHub-backed remotes, and deployment governance
**Confidence:** HIGH

<user_constraints>
## User Constraints

### Locked Decisions
- Keep the infrastructure simple and top-level.
- GitHub is optional; it must not be treated as mandatory without strong reason.
- A Tailscale-reachable server is acceptable if it can serve as a reliable Git remote.
- cPanel and SSH are already operational and should remain deployment paths, but not become the code source of truth.
- Repo hierarchy must avoid per-app sprawl and keep program/app ownership obvious.

### Verified Baseline
- The current Lavprishjemmeside provisioning and release scripts already assume Git-backed deployable repos and rollback by commit SHA.
- `lavprishjemmeside.dk`, `ljdesignstudio.dk`, and `reporting.theartisan.dk` behave like independent live deploy surfaces.
- The clean AI-Enterprise target currently governs portfolio structure locally, but it does not yet have a locked remote Git topology.
- GitHub SSH auth is currently missing on the workstation, while public HTTPS fetch works.

### Deferred Ideas
- Migrating off cPanel in this phase.
- Building a large CI/CD platform before source-of-truth and repo boundaries are locked.
- Splitting every placeholder or internal module into its own repo.

</user_constraints>

<research_summary>
## Summary

The core question is not "GitHub or local." The real question is: what system records the canonical history of code and infrastructure decisions, and how does that history reach the live servers safely?

**Primary recommendation:** Git must be the source of truth. GitHub is optional. For this portfolio, the best-fit operating model is:

1. **local-first development**
2. **self-hosted primary Git remote reachable over Tailscale**
3. **cPanel/SSH as deploy targets only**
4. **optional GitHub mirror for backup, collaboration, and future CI**

That model preserves local control, removes GitHub as a hard dependency, and still keeps the critical engineering guarantees that direct-to-live editing cannot provide: versioned history, rollback, traceability, and reproducible deploys.

The strongest reason not to build directly into live versions is not ideology. It is operational safety. Your existing live rollout already depends on Git semantics. The moment cPanel becomes the primary source of truth, you lose commit-based rollback, drift detection, and a clean answer to "what code is live right now?"

The repo topology should stay shallow:

- one main repo for `AI-Enterprise`
- one repo per independently deployed live surface
- no nested repos inside `AI-Enterprise`
- no repo per placeholder, per dashboard tab, or per internal module unless it becomes an independent deploy unit

**Recommended final posture:** self-hosted Git over Tailscale as primary, GitHub optional as mirror, and cPanel never authoritative for source.
</research_summary>

<standard_stack>
## Standard Stack

### Core
| Layer | Recommended Standard | Why |
|-------|----------------------|-----|
| Source of truth | Git repository history | Gives commits, rollback, traceability, and reproducible deploy state |
| Primary remote | Self-hosted Git server over Tailscale SSH | Keeps control private and local-first without depending on GitHub |
| Optional secondary remote | GitHub mirror | Adds offsite redundancy, collaboration, and future Actions/PR workflows |
| Deploy transport | SSH to cPanel and related hosts | Matches current operational reality |
| Deploy target | remote working tree or release checkout from Git | Keeps live hosts downstream from source-of-truth Git history |

### Supporting
| Tool | Purpose | Why It Matters |
|------|---------|----------------|
| Tailscale SSH | private transport to the Git host | makes a self-hosted remote practical without public exposure |
| `git ls-remote` and `git fetch --all` | remote health validation | proves remotes are reachable and history is intact |
| current Lavprishjemmeside release scripts | real-world deploy evidence | they already assume repo existence and commit rollback |
| cPanel validation scripts | post-deploy safety net | confirms that deploy targets remain healthy after changes |

### Alternatives Considered
| Model | Strength | Weakness |
|-------|----------|----------|
| GitHub as primary remote | easy collaboration and hosted durability | external dependency, overkill if governance remains private and local |
| Self-hosted Git over Tailscale | local control, private access, simple SSH operations | requires your own backup and availability discipline |
| Direct edits on live cPanel | lowest short-term friction | no clean source of truth, weak rollback, high drift risk |
| Hybrid primary self-hosted + GitHub mirror | best resilience and optional collaboration | slightly more operational setup |

</standard_stack>

<architecture_patterns>
## Architecture Patterns

### Pattern 1: Git Provider Agnostic Source Of Truth
**What:** treat Git history as canonical, while leaving the hosting provider interchangeable.
**When to use:** always for AI-Enterprise and any actively governed live surface.
**Why:** it solves the GitHub-versus-Tailscale question cleanly. GitHub is a hosting choice, not the architecture.

### Pattern 2: Repo Per Deploy Boundary
**What:** create a separate repo only when a codebase has its own runtime, its own deploy/rollback cycle, or its own operator/client boundary.
**When to use:** `AI-Enterprise`, `lavprishjemmeside.dk`, `ljdesignstudio.dk`, `reporting.theartisan.dk`, and possibly custom `theartisan` theme/plugin code if it is truly maintained independently.
**Why:** this keeps repos aligned with real operational units instead of arbitrary app labels.

### Pattern 3: Remote-First Portfolio Modeling Without Nested Git
**What:** AI-Enterprise stores manifests, docs, and registry metadata for remote-first repos rather than checking those repos in as nested working trees.
**When to use:** for client sites and remote deploy surfaces already living outside the core control-plane repo.
**Why:** nested repos blur boundaries and make top-level Git hygiene harder.

### Pattern 4: Deploy-Target-Only Hosts
**What:** cPanel servers receive deploys and health checks, but code changes land in Git first.
**When to use:** always, except emergency live hotfixes that are immediately backported.
**Why:** deploy servers are poor source-of-truth systems because they do not naturally provide safe review, history discovery, or rollback discipline.

### Anti-Patterns To Avoid
- treating GitHub as mandatory when the actual need is simply a stable Git remote
- storing live working trees for independent sites inside `AI-Enterprise/programs/` as nested repos
- repo-per-app for placeholders, dashboards, or context-only modules
- editing cPanel live files as the normal workflow
- coupling source-of-truth decisions to whichever host currently happens to be reachable

</architecture_patterns>

<dont_hand_roll>
## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| source-of-truth policy | unwritten operator convention | explicit docs plus validation scripts | the policy must be testable |
| repo classification | ad hoc per-program decisions | one manifest that marks each surface as `main`, `independent`, `embedded`, or `archive` | prevents future repo sprawl |
| deployment provenance | "latest code on server" reasoning | Git SHA recorded in deploy manifests or release logs | answers what is live |
| backup strategy | trust one box forever | primary remote plus snapshot/mirror policy | self-hosted Git must still be durable |

**Key insight:** the simplest correct model is not "everything in one repo" or "everything in GitHub." It is "one authoritative Git history per true deploy boundary, with the smallest number of repos that still preserves rollback and ownership."
</dont_hand_roll>

<common_pitfalls>
## Common Pitfalls

### Pitfall 1: Using Tailscale as if it were version control
**What goes wrong:** the team says "we have Tailscale" but still has no canonical remote, no mirror, and no backup policy.
**How to avoid:** treat Tailscale as the secure transport to the Git host, not as the source-of-truth mechanism itself.

### Pitfall 2: Letting cPanel become the real source of truth
**What goes wrong:** production fixes land only on the server and never make it back into Git, so history and live state diverge.
**How to avoid:** require every live hotfix to be backported immediately and reject routine direct edits.

### Pitfall 3: Creating repos for every app label
**What goes wrong:** placeholders and internal modules get their own repos, which creates ownership drift and empty maintenance overhead.
**How to avoid:** use deploy boundary, rollback boundary, and client ownership as the split criteria.

### Pitfall 4: Keeping remote-first sites nested under AI-Enterprise
**What goes wrong:** the main repo starts pretending to own external working trees, leading to nested Git confusion and accidental duplication.
**How to avoid:** represent them via manifests, docs, and validation contracts instead of nested clones.

### Pitfall 5: Self-hosting Git without durability
**What goes wrong:** the self-hosted server is correct architecturally but fragile operationally because it has no backup or mirror.
**How to avoid:** define backup and mirror policy in the same phase as the topology.

</common_pitfalls>

<recommended_topology>
## Recommended Topology

### Repo Topology
- `AI-Enterprise` — main control-plane repo
- `lavprishjemmeside.dk` — independent live CMS/template/governance surface
- `ljdesignstudio.dk` — independent governed client surface
- `reporting.theartisan.dk` — independent reporting surface
- optional `the-artisan-custom` repo only if custom WordPress code is still actively developed separately

### Not Separate Repos By Default
- `personal-assistant/*` placeholders
- Samlino context modules unless promoted into standalone live surfaces
- internal dashboard subsections inside the same runtime
- archive or migration-hold payloads

### Top-Level Folder Hierarchy

For the main workspace:

```text
/Users/IAn/Agent/
|-- AI-Enterprise/          # main control-plane repo
|-- sites/
|   |-- lavprishjemmeside.dk/
|   |-- ljdesignstudio.dk/
|   `-- reporting.theartisan.dk/
`-- archive/                # optional, non-live or migration-hold material
```

For the self-hosted Git server:

```text
/srv/git/
|-- AI-Enterprise.git
|-- lavprishjemmeside.dk.git
|-- ljdesignstudio.dk.git
`-- reporting.theartisan.dk.git
```

This is intentionally shallow. No nested repos inside the main repo.
</recommended_topology>

<recommended_phase_split>
## Recommended Phase Split

### Plan 09-01: Lock the canonical infrastructure model and repo topology
- define the source-of-truth contract
- decide primary remote strategy: self-hosted over Tailscale, with optional GitHub mirror
- classify every current program/app as `main repo`, `independent repo`, `embedded`, or `archive`
- document the top-level folder hierarchy and no-nested-repos rule

### Plan 09-02: Build the governance and validation scaffolding
- create manifests, runbooks, and bootstrap scripts for the chosen Git topology
- add validation scripts for remote reachability, rollback readiness, and deploy-target drift
- connect cPanel deployment checks to commit-based provenance

This split keeps architecture decisions stable before scripting the operational guardrails.
</recommended_phase_split>

## Validation Architecture

Phase 9 validation should prove:

- there is a single documented source-of-truth rule and it names Git, not GitHub or cPanel, as the invariant
- the selected primary remote model works with either GitHub or a Tailscale-hosted Git server
- every current program/app is classified into repo topology buckets with no ambiguous cases
- the main repo does not contain nested working trees for independently deployed live sites
- deploy validation scripts can prove remote reachability, rollback capability, and cPanel health
- the resulting top-level hierarchy stays shallow and operator-readable

<sources>
## Sources

### Primary (HIGH confidence)
- `/Users/IAn/Agent/AI-Enterprise/.planning/phases/09-infrastructure-topology-git-source-of-truth-and-deployment-governance-simplification/09-CONTEXT.md`
- `/Users/IAn/Agent/AI-Enterprise/.planning/REQUIREMENTS.md`
- `/Users/IAn/Agent/AI-Enterprise/.planning/STATE.md`
- `/Users/IAn/Agent/IAn/scripts/lavpris/ssh_client_install.sh`
- `/Users/IAn/Agent/IAn/scripts/lavpris/ssh_release_preflight.sh`
- `/Users/IAn/Agent/AI-Enterprise/programs/lavprishjemmeside/README.md`
- `/Users/IAn/Agent/AI-Enterprise/programs/lavprishjemmeside/cms/README.md`
- `/Users/IAn/Agent/AI-Enterprise/programs/lavprishjemmeside/client-sites/ljdesignstudio.dk/README.md`
- `/Users/IAn/Agent/AI-Enterprise/.planning/codebase/INTEGRATIONS.md`
- `/Users/IAn/Agent/AI-Enterprise/.planning/codebase/STRUCTURE.md`
- `/Users/IAn/Agent/AI-Enterprise/.planning/codebase/CONCERNS.md`

### External (HIGH confidence)
- GitHub `CODEOWNERS`: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners
- GitHub protected branches: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- GitHub environments: https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments
- Tailscale SSH: https://tailscale.com/kb/1193/tailscale-ssh
- Git clone URL forms: https://git-scm.com/docs/git-clone

</sources>

<metadata>
## Metadata

**Research scope:**
- source of truth
- GitHub versus self-hosted Git
- Tailscale applicability
- repo boundaries
- deploy-target governance

**Confidence breakdown:**
- local operational baseline: HIGH
- GitHub governance capabilities: HIGH
- Tailscale transport role: HIGH
- recommended repo topology: HIGH
- exact self-hosted Git product choice: MEDIUM

**Research date:** 2026-03-08
**Valid until:** 2026-04-07
</metadata>

---

*Phase: 09-infrastructure-topology-git-source-of-truth-and-deployment-governance-simplification*
*Research completed: 2026-03-08*
*Ready for planning: yes*
