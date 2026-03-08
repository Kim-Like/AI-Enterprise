# AI-Enterprise Portfolio Structure

## Governing Layer

- `IAn Agency`

## Top-Level Program Lanes

1. `Lavprishjemmeside`
2. `Artisan`
3. `Baltzer Games`
4. `Personal assistance`

## Program Notes

### Lavprishjemmeside

- remote-first program
- explicitly organized as `cms/` plus `client-sites/`
- governed client sites currently include:
  - `lavprishjemmeside.dk`
  - `ljdesignstudio.dk`

### Artisan

- reporting app
- WordPress/B2B site
- email marketing workspace

### Baltzer Games

- TCG index
- reporting
- Shopify and placeholder product tracks
- TCG index is represented as a migration-hold contract, not a live workload

### Personal assistance

- preserved as a skeleton suite with five placeholder modules

## IAn Agency Contexts

Assets that remain strategically relevant but are not top-level client programs are carried under:

- `programs/ian-agency/contexts/`

Current example:

- `samlino/seo-agent-playground`

The Samlino submodules `AI-visibility`, `seo-auditor`, and `samlino-mind-map` are archive-mapped explicitly so they remain visible as context without being promoted as live clean-target payloads.

## Git Governance

- Git is the code source of truth.
- Independent live surfaces are classified in `ops/repository-topology.json`.
- `AI-Enterprise` keeps docs and manifests for remote-first sites; it does not store nested checked-out repos for them.
