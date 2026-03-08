# AI-Enterprise Infrastructure Topology

## Core Rule

Git is the canonical source of truth for code and infrastructure definitions.

GitHub under the `Kim-Like` namespace is the primary remote.

cPanel, SSH-accessible app servers, and remote working trees are deploy targets only. They are never the long-term authoring truth for code.

## Recommended Operating Model

### Primary Remote

- GitHub repositories under `git@github.com:Kim-Like/...`
- SSH-authenticated access for push, fetch, and bootstrap
- commit history used for rollback and provenance

### Optional Secondary Remote

- self-hosted bare Git repositories on a Tailscale-reachable host
- optional offsite or private redundancy
- not required for day-to-day operation
- may be added later without changing the local folder topology

### Deploy Targets

- cPanel-hosted sites and APIs
- local backend-served dashboard
- any future staging host

Deploy targets consume versioned code from Git. They do not define what the code should be.

## Why This Model

- It preserves local control while keeping the remote model simple and explicit.
- It keeps the remote topology simple: one public provider namespace, no split-brain primary.
- It keeps the code history independent from the deployment platform.
- It matches the current Lavprishjemmeside release model, which already depends on Git clones and commit rollback.
- It avoids nested-repo sprawl inside `AI-Enterprise`.

## Top-Level Workspace Layout

```text
/Users/IAn/Agent/
|-- AI-Enterprise/          # main control-plane repo
|-- sites/                  # optional local clones of independent live surfaces
|   |-- lavprishjemmeside.dk/
|   |-- ljdesignstudio.dk/
|   `-- reporting.theartisan.dk/
`-- archive/                # non-live or migration-hold material
```

This layout is intentionally shallow. The operator should understand the whole portfolio from the first directory listing.

## GitHub Repository Layout

```text
github.com/Kim-Like/
|-- AI-Enterprise
|-- lavprishjemmeside.dk
|-- ljdesignstudio.dk
`-- reporting.theartisan.dk
```

These repositories are the primary remote endpoints. Working trees or release checkouts on app hosts are downstream from them.

## Autonomy Provisioning

Wave 1 extends `ops/repository-topology.json` with per-repository `primary_remote` and `autonomy` metadata.

That metadata does not replace the Phase 9 env contract. `*_PRIMARY_GIT_REMOTE` remains the runtime override when a remote is already configured, while the manifest remains the canonical desired-state contract for governed remote provisioning preflight.

See `docs/autonomy-provisioning.md` for the Wave 1 policy and dry-run rules.

## Repo Boundaries

### Main Repo

- `AI-Enterprise`

### Independent Repos

- `lavprishjemmeside.dk`
- `ljdesignstudio.dk`
- `reporting.theartisan.dk`

### Embedded In `AI-Enterprise`

- Samlino agency context
- Personal assistant placeholders
- Baltzer placeholders and migration-hold payloads
- control-plane-specific docs, agents, API, and runtime

## Rules

1. No nested Git working trees inside `AI-Enterprise`.
2. A new repo is created only when a surface has its own deploy boundary or rollback boundary.
3. Emergency live edits are allowed only if they are immediately backported into Git.
4. Remote-first sites are represented inside `AI-Enterprise` by manifests, docs, and health contracts, not by nested clones.
5. Data stores may remain remote system-of-records for app data, but code history always lives in Git.

## Canonical References

- Topology manifest: `ops/repository-topology.json`
- Governance policy: `docs/repository-governance.md`
- Deploy provenance: `docs/deployment-provenance.md`
- Autonomy provisioning: `docs/autonomy-provisioning.md`
