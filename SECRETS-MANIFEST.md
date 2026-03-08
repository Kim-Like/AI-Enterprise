# Secrets Manifest

No values belong in this file. It is the clean target's canonical inventory of required secret and connection variables.

## P0

| Secret Name | Provider/Purpose | Required For | Priority |
|-------------|------------------|--------------|----------|
| `DASHBOARD_ADMIN_KEY` | AI-Enterprise operator admin access | Settings and control-plane writes | P0 |
| `IAN_AUTONOMY_KEY` | AI-Enterprise autonomy access | Controlled automation writes | P0 |
| `ANTHROPIC_API_KEY` | Anthropic Claude API access | IAn and agent model operations | P0 |
| `OPENAI_API_KEY` | OpenAI API access | Engineer and fallback model operations | P0 |
| `CPANEL_API_TOKEN` | cPanel API access | Remote deployment and reporting operations | P0 |
| `CPANEL_SSH_HOST` | cPanel SSH host config | Remote deploy and diagnostics | P0 |
| `CPANEL_SSH_PORT` | cPanel SSH port config | Remote deploy and diagnostics | P0 |
| `CPANEL_SSH_USER` | cPanel SSH user config | Remote deploy and diagnostics | P0 |
| `CPANEL_SSH_KEY_PATH` | cPanel SSH key path | Remote deploy and diagnostics | P0 |
| `ARTISAN_REPORTING_DB_HOST` | Artisan reporting DB host | Artisan reporting MySQL | P0 |
| `ARTISAN_REPORTING_DB_PORT` | Artisan reporting DB port | Artisan reporting MySQL | P0 |
| `ARTISAN_REPORTING_DB_NAME` | Artisan reporting DB name | Artisan reporting MySQL | P0 |
| `ARTISAN_REPORTING_DB_USER` | Artisan reporting DB user | Artisan reporting MySQL | P0 |
| `ARTISAN_REPORTING_DB_PASSWORD` | Artisan reporting DB password | Artisan reporting MySQL | P0 |
| `ARTISAN_WP_DB_HOST` | Artisan WordPress DB host | Artisan WordPress MySQL | P0 |
| `ARTISAN_WP_DB_NAME` | Artisan WordPress DB name | Artisan WordPress MySQL | P0 |
| `ARTISAN_WP_DB_USER` | Artisan WordPress DB user | Artisan WordPress MySQL | P0 |
| `ARTISAN_WP_DB_PASSWORD` | Artisan WordPress DB password | Artisan WordPress MySQL | P0 |

## P1

| Secret Name | Provider/Purpose | Required For | Priority |
|-------------|------------------|--------------|----------|
| `BILLY_API_TOKEN` | Billy API access | Reporting integrations | P1 |
| `SHOPIFY_STORE_DOMAIN` | Shopify store domain | Baltzer Shopify configuration | P1 |
| `SHOPIFY_ADMIN_TOKEN` | Shopify admin API token | Baltzer Shopify backend operations | P1 |
| `DB_HOST` | Lavprishjemmeside DB host | Lavprishjemmeside CMS MySQL | P1 |
| `DB_NAME` | Lavprishjemmeside DB name | Lavprishjemmeside CMS MySQL | P1 |
| `DB_USER` | Lavprishjemmeside DB user | Lavprishjemmeside CMS MySQL | P1 |
| `DB_PASSWORD` | Lavprishjemmeside DB password | Lavprishjemmeside CMS MySQL | P1 |

## P2

| Secret Name | Provider/Purpose | Required For | Priority |
|-------------|------------------|--------------|----------|
| `OAUTH_CLIENT_ID_*` | Future operator sign-in client IDs | Optional operator auth expansion | P2 |
| `WEBHOOK_SIGNING_SECRET_*` | Future webhook verification | Optional inbound/outbound webhooks | P2 |
| `STAGING_*` | Non-production integration credentials | Staging/test environments | P2 |

## Storage Policy

- Local development uses `.env.local`.
- Shared environments should use a secrets manager.
- `.env.example` contains names only and no real values.
- Frontend exposure is limited to explicitly safe client identifiers; secret keys and admin/autonomy credentials must remain server-only.
