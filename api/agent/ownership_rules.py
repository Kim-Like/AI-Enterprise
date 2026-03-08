"""Deterministic objective routing and program ownership rules."""
from typing import Dict, List, Optional, Sequence, Tuple

VALID_MASTER_IDS = {
    "father",
    "engineer",
    "ian-master",
    "artisan-master",
    "lavprishjemmeside-master",
    "samlino-master",
    "personal-assistant-master",
    "baltzer-master",
}

MASTER_ROUTING_RULES: Sequence[Tuple[str, Sequence[str]]] = (
    (
        "engineer",
        (
            "error",
            "bug",
            "infra",
            "incident",
            "fix",
            "security",
            "deploy",
            "timeout",
            "exception",
        ),
    ),
    (
        "artisan-master",
        (
            "artisan",
            "cafe",
            "the artisan",
            "saren",
            "wordpress",
            "wp",
            "b2b",
            "brevo",
            "reporting.theartisan.dk",
        ),
    ),
    (
        "lavprishjemmeside-master",
        (
            "lavprishjemmeside",
            "lavpris",
            "ai cms",
            "ads dashboard",
            "seo dashboard",
            "subscription",
            "client overview",
        ),
    ),
    (
        "samlino-master",
        (
            "samlino",
            "seo-agent-playground",
            "comparaja",
            "product management",
            "ai visibility",
        ),
    ),
    (
        "personal-assistant-master",
        (
            "personal assistant",
            "calendar",
            "task manager",
            "email management",
            "social media",
            "apple watch",
            "fitness",
        ),
    ),
    (
        "baltzer-master",
        (
            "baltzer",
            "shopify",
            "tcg",
            "event",
            "employee schedule",
            "salary api",
            "reporting.baltzergames.dk",
        ),
    ),
    (
        "father",
        (
            "ian",
            "portfolio",
            "pmo",
            "governance",
            "cross-program",
            "cross program",
            "system architecture",
        ),
    ),
)

MASTER_PROGRAMS: Dict[str, List[str]] = {
    "father": ["ian-control-plane"],
    "engineer": [
        "ian-control-plane",
        "artisan-reporting",
        "artisan-wordpress",
        "artisan-email-marketing",
        "lavprishjemmeside-cms",
        "samlino-seo-agent-playground",
        "baltzer-tcg-index",
        "baltzer-reporting",
        "baltzer-shopify",
        "personal-assistant-suite",
    ],
    "ian-master": ["ian-control-plane"],
    "artisan-master": [
        "artisan-reporting",
        "artisan-wordpress",
        "artisan-email-marketing",
    ],
    "lavprishjemmeside-master": ["lavprishjemmeside-cms"],
    "samlino-master": ["samlino-seo-agent-playground"],
    "personal-assistant-master": ["personal-assistant-suite"],
    "baltzer-master": [
        "baltzer-tcg-index",
        "baltzer-reporting",
        "baltzer-shopify",
    ],
}

PROGRAM_SCOPE_PATHS: Dict[str, str] = {
    "ian-control-plane": ".",
    "artisan-reporting": "programs/artisan/reporting.theartisan.dk",
    "artisan-wordpress": "programs/artisan/the-artisan-wp",
    "artisan-email-marketing": "programs/artisan/e-mail-marketing",
    "lavprishjemmeside-cms": "ssh://theartis@cp10.nordicway.dk/home/theartis/repositories/lavprishjemmeside.dk",
    "samlino-seo-agent-playground": "programs/ian-agency/contexts/samlino/seo-agent-playground",
    "baltzer-tcg-index": "programs/baltzer/TCG-index",
    "baltzer-reporting": "programs/baltzer/reporting.baltzergames.dk",
    "baltzer-shopify": "programs/baltzer/shopify",
    "personal-assistant-suite": "programs/personal-assistant",
}


def validate_master(master_id: str) -> Optional[str]:
    normalized = (master_id or "").strip().lower()
    if normalized in VALID_MASTER_IDS:
        return normalized
    return None
