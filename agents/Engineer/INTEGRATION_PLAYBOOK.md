# Integration Playbook

## Integration Principle

Treat `father.db` as control-plane state only. Keep all business app data in native app stores.

## Lavprishjemmeside (MySQL on cPanel)

- Required env:
  - `DB_HOST`
  - `DB_USER`
  - `DB_PASSWORD`
  - `DB_NAME`
- Validate with `/api/datastores/verify` after changes.

## Artisan WordPress (cPanel MySQL)

- Required env:
  - `ARTISAN_WP_DB_HOST`
  - `ARTISAN_WP_DB_USER`
  - `ARTISAN_WP_DB_PASSWORD`
  - `ARTISAN_WP_DB_NAME`
- Do not alter production WP DB contracts without rollback plan.

## Reporting Apps (Artisan/Baltzer)

- Preserve local JSON state in each app `data/` path.
- Protect `BILLY_API_TOKEN` handling.
- Keep brand-specific configuration separated.

## Demoted Datastore Workloads

- Samlino is SQLite-backed in the clean target.
- Baltzer TCG is a migration-hold workload until a local datastore replacement is implemented.
- Do not reintroduce third-party datastore credentials into AI-Enterprise.

## Shopify

- Required env:
  - `SHOPIFY_STORE_DOMAIN`
  - `SHOPIFY_ADMIN_TOKEN`
- Keep token scope minimal and rotate periodically.

## Validation Standard

After integration changes:

1. run tests
2. run `/api/datastores/verify`
3. confirm no new open errors in `error_log`
