# AI-Enterprise Repository Governance

## Classification Model

Every surface belongs to one of four repository buckets:

- `main`: the primary control-plane repository
- `independent`: a surface that deserves its own repo because it has its own deploy or rollback boundary
- `embedded`: code or context that lives inside another repo
- `archive`: non-live or migration-hold material that should not drive active repo creation

The machine-readable source for these assignments is `ops/repository-topology.json`.

## Decision Rules

Create a separate repo only when all of these are true:

1. The surface has its own live runtime or deploy cycle.
2. Rollback may need to happen independently of the control plane.
3. The surface is operated or reasoned about as its own product or client property.

Keep a surface embedded when any of these are true:

1. It is a placeholder, scaffold, or planned module.
2. It shares the same deploy boundary as a parent surface.
3. It is context, documentation, or a migration-hold payload.

Archive a surface when any of these are true:

1. It is intentionally non-live.
2. It is preserved only for traceability.
3. It should not receive active Git governance yet.

## Current Repo Assignments

| Repo ID | Bucket | Role |
|---------|--------|------|
| `ai-enterprise` | `main` | control plane, agents, docs, orchestration, portfolio registry |
| `lavprishjemmeside.dk` | `independent` | parent CMS/template/governance surface |
| `ljdesignstudio.dk` | `independent` | governed client-site surface |
| `reporting.theartisan.dk` | `independent` | reporting runtime with its own health endpoint |

## Git Provider Policy

- Primary remote is GitHub over SSH under the `Kim-Like` namespace.
- A Tailscale-reachable bare Git mirror may be added later if private redundancy is needed.
- The provider is replaceable; the Git history is the invariant.

## Local Workflow

1. Work locally.
2. Commit to Git.
3. Push to the primary remote.
4. Optionally mirror to a private secondary remote.
5. Deploy to cPanel or another target from versioned Git history.
6. Run validation and health checks.

## No-Nested-Repos Rule

`AI-Enterprise` must not contain nested checked-out repos for independent live surfaces.

Allowed representation inside `AI-Enterprise`:

- docs
- manifests
- ownership metadata
- health/validation contracts

Not allowed inside `AI-Enterprise`:

- checked-out Git working trees for `lavprishjemmeside.dk`
- checked-out Git working trees for `ljdesignstudio.dk`
- checked-out Git working trees for `reporting.theartisan.dk`

## Hotfix Rule

If a production hotfix is made directly on a live host:

1. capture the exact file and change
2. backport it into the authoritative Git repo immediately
3. record the resulting commit in the deploy provenance log

Live-only edits are an exception path, not an operating model.
