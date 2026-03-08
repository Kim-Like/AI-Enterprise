"""Canonical secret inventory for AI-Enterprise."""
from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class SecretDefinition:
    name: str
    provider: str
    purpose: str
    required_for: str
    priority: str
    scope: str = "server"
    kind: str = "secret"


SECRET_DEFINITIONS = (
    SecretDefinition("DASHBOARD_ADMIN_KEY", "AI-Enterprise", "Operator admin access", "Admin settings and control-plane writes", "P0"),
    SecretDefinition("IAN_AUTONOMY_KEY", "AI-Enterprise", "Autonomy write access", "Controlled automation writes", "P0"),
    SecretDefinition("ANTHROPIC_API_KEY", "Anthropic", "Claude API access", "IAn and agent model operations", "P0"),
    SecretDefinition("OPENAI_API_KEY", "OpenAI", "OpenAI API access", "Engineer and fallback model operations", "P0"),
    SecretDefinition("CPANEL_API_TOKEN", "cPanel", "cPanel API access", "Remote deployment and reporting operations", "P0"),
    SecretDefinition("CPANEL_SSH_HOST", "cPanel", "SSH host target", "Remote deploy and diagnostics", "P0", kind="config"),
    SecretDefinition("CPANEL_SSH_PORT", "cPanel", "SSH port target", "Remote deploy and diagnostics", "P0", kind="config"),
    SecretDefinition("CPANEL_SSH_USER", "cPanel", "SSH user target", "Remote deploy and diagnostics", "P0", kind="config"),
    SecretDefinition("CPANEL_SSH_KEY_PATH", "cPanel", "SSH private key path", "Remote deploy and diagnostics", "P0", kind="config"),
    SecretDefinition("ARTISAN_REPORTING_DB_HOST", "Artisan Reporting", "Database host", "Artisan reporting MySQL", "P0", kind="config"),
    SecretDefinition("ARTISAN_REPORTING_DB_PORT", "Artisan Reporting", "Database port", "Artisan reporting MySQL", "P0", kind="config"),
    SecretDefinition("ARTISAN_REPORTING_DB_NAME", "Artisan Reporting", "Database name", "Artisan reporting MySQL", "P0", kind="config"),
    SecretDefinition("ARTISAN_REPORTING_DB_USER", "Artisan Reporting", "Database user", "Artisan reporting MySQL", "P0", kind="config"),
    SecretDefinition("ARTISAN_REPORTING_DB_PASSWORD", "Artisan Reporting", "Database password", "Artisan reporting MySQL", "P0"),
    SecretDefinition("ARTISAN_WP_DB_HOST", "Artisan WordPress", "Database host", "Artisan WordPress MySQL", "P0", kind="config"),
    SecretDefinition("ARTISAN_WP_DB_NAME", "Artisan WordPress", "Database name", "Artisan WordPress MySQL", "P0", kind="config"),
    SecretDefinition("ARTISAN_WP_DB_USER", "Artisan WordPress", "Database user", "Artisan WordPress MySQL", "P0", kind="config"),
    SecretDefinition("ARTISAN_WP_DB_PASSWORD", "Artisan WordPress", "Database password", "Artisan WordPress MySQL", "P0"),
    SecretDefinition("BILLY_API_TOKEN", "Billy", "Billy accounting API", "Artisan and Baltzer reporting sync", "P1"),
    SecretDefinition("SHOPIFY_STORE_DOMAIN", "Shopify", "Shopify store domain", "Baltzer Shopify config", "P1", kind="config"),
    SecretDefinition("SHOPIFY_ADMIN_TOKEN", "Shopify", "Shopify admin token", "Baltzer Shopify backend access", "P1"),
    SecretDefinition("DB_HOST", "Lavprishjemmeside", "Database host", "Lavprishjemmeside CMS MySQL", "P1", kind="config"),
    SecretDefinition("DB_NAME", "Lavprishjemmeside", "Database name", "Lavprishjemmeside CMS MySQL", "P1", kind="config"),
    SecretDefinition("DB_USER", "Lavprishjemmeside", "Database user", "Lavprishjemmeside CMS MySQL", "P1", kind="config"),
    SecretDefinition("DB_PASSWORD", "Lavprishjemmeside", "Database password", "Lavprishjemmeside CMS MySQL", "P1"),
)

SECRET_DEFINITIONS_BY_NAME = {item.name: item for item in SECRET_DEFINITIONS}


def secret_definition_rows() -> list[dict[str, str]]:
    return [asdict(item) for item in SECRET_DEFINITIONS]
