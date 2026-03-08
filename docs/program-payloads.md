# Program Payload Duplication Manifest

## Canonical Program Roots Copied

| Program ID | Source Root | Target Root | Notes |
|------------|-------------|-------------|-------|
| `artisan-reporting` | `programs/artisan/reporting.theartisan.dk` | `AI-Enterprise/programs/artisan/reporting.theartisan.dk` | nested duplicate `the-artisan-wp` excluded |
| `artisan-wordpress` | `programs/artisan/the-artisan-wp` | `AI-Enterprise/programs/artisan/the-artisan-wp` | uploads/plugins/vendor/build excluded; theme payload preserved |
| `artisan-email-marketing` | `programs/artisan/e-mail-marketing` | `AI-Enterprise/programs/artisan/e-mail-marketing` | placeholder/lightweight payload |
| `lavprishjemmeside-cms` | SSH-first source | `AI-Enterprise/programs/lavprishjemmeside` | remote-first program now modeled as `cms/` plus governed `client-sites/` |
| `samlino-seo-agent-playground` | `programs/samlino/seo-agent-playground` | `AI-Enterprise/programs/ian-agency/contexts/samlino/seo-agent-playground` | context workspace rehomed under `IAn Agency` to match the target operating model |
| `baltzer-tcg-index` | `programs/baltzer/TCG-index` | `AI-Enterprise/programs/baltzer/TCG-index` | demoted to explicit migration-hold contract pending local datastore replacement |
| `baltzer-reporting` | `programs/baltzer/reporting.baltzergames.dk` | `AI-Enterprise/programs/baltzer/reporting.baltzergames.dk` | copied with nested repo/cache exclusions |
| `baltzer-shopify` | `programs/baltzer/shopify` | `AI-Enterprise/programs/baltzer/shopify` | sparse source preserved as-is |
| `baltzer-social-media-management` | `programs/baltzer/social-media-management` | `AI-Enterprise/programs/baltzer/social-media-management` | placeholder scaffold preserved |
| `baltzer-event-management-platform` | `programs/baltzer/event-management-platform` | `AI-Enterprise/programs/baltzer/event-management-platform` | placeholder scaffold preserved |
| `baltzer-employee-schedule-salary-api` | `programs/baltzer/employee-schedule-salary-api` | `AI-Enterprise/programs/baltzer/employee-schedule-salary-api` | placeholder scaffold preserved |
| `personal-assistant-suite` | `programs/personal-assistant` | `AI-Enterprise/programs/personal-assistant` | placeholder app scaffolds preserved |

## Explicit Exclusions

- nested `.git` directories
- `node_modules`
- `venv` and `.venv`
- `__pycache__` and `.pytest_cache`
- `dist` and `build`
- `vendor`
- WordPress `wp-content/uploads`
- WordPress `wp-content/plugins`
- dangerous duplicate or vendor payloads:
  - `AI-Visibility copy`
- nested duplicate `programs/artisan/reporting.theartisan.dk/the-artisan-wp`

## Archive-Mapped Context

Some source submodules are intentionally represented as archive context instead of live duplicated payload:

- `programs/ian-agency/contexts/samlino/seo-agent-playground/AI-visibility`
- `programs/ian-agency/contexts/samlino/seo-agent-playground/seo-auditor`
- `programs/ian-agency/contexts/samlino/seo-agent-playground/samlino-mind-map`

These entries keep operational traceability without reintroducing brownfield code paths that violate the clean-target contract.

## Remote-First Rule

Where the source system itself is SSH-first without canonical local payload, the target models the governing structure explicitly instead of inventing a fake local implementation.

## Repository Topology Rule

Remote-first live surfaces are represented in `ops/repository-topology.json` and related docs. They remain outside the `AI-Enterprise` working tree as independent repos or deploy targets, never as nested checked-out repos.
