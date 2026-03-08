# cPanel Runtime Contract

## Policy

- runtime secrets belong in server-side `.env` files or the host secret store
- `.htaccess` and equivalent cPanel config files may contain routing directives only
- deployment automation must never template secrets into cPanel config files

## Guardrails

- `scripts/check_remote_config_contract.sh` scans the live cPanel config file locations for forbidden secret-bearing directives
- `scripts/verify_remote_portfolio.sh` rechecks the live health endpoints after portfolio changes
- `scripts/validate_ai_enterprise.sh` runs both scripts after the local frontend/backend suite

## Domains Covered

- `lavprishjemmeside.dk`
- `ljdesignstudio.dk`
- `reporting.theartisan.dk`

## Allowed Pattern

- route or runtime selection directives only
- secret-bearing environment files on the server remain acceptable
- any `SetEnv`, `PassengerEnvVar`, token, password, key, or secret literal in cPanel config is a release blocker
