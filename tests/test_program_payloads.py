from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path("/Users/IAn/Agent/AI-Enterprise")


def test_canonical_program_roots_exist():
    expected = [
        "programs/ian-agency",
        "programs/artisan/reporting.theartisan.dk",
        "programs/artisan/e-mail-marketing",
        "programs/artisan/the-artisan-wp",
        "programs/baltzer/TCG-index",
        "programs/baltzer/reporting.baltzergames.dk",
        "programs/baltzer/shopify",
        "programs/personal-assistant",
        "programs/ian-agency/contexts/samlino/seo-agent-playground",
        "programs/lavprishjemmeside",
    ]
    for rel in expected:
        assert (PROJECT_ROOT / rel).exists(), rel


def test_placeholder_and_manifest_artifacts_exist():
    assert (PROJECT_ROOT / "programs" / "lavprishjemmeside" / "README.md").exists()
    assert (PROJECT_ROOT / "programs" / "lavprishjemmeside" / "cms" / "README.md").exists()
    assert (PROJECT_ROOT / "programs" / "lavprishjemmeside" / "client-sites" / "lavprishjemmeside.dk" / "README.md").exists()
    assert (PROJECT_ROOT / "programs" / "lavprishjemmeside" / "client-sites" / "ljdesignstudio.dk" / "README.md").exists()
    assert (PROJECT_ROOT / "programs" / "baltzer" / "TCG-index" / "MIGRATION-HOLD.md").exists()
    assert (PROJECT_ROOT / "docs" / "portfolio-structure.md").exists()
    manifest = PROJECT_ROOT / "docs" / "program-payloads.md"
    assert manifest.exists()
    text = manifest.read_text()
    assert "remote-first program now modeled as `cms/` plus governed `client-sites/`" in text
    assert "archive context" in text
    assert "migration-hold contract" in text


def test_samlino_context_is_archive_mapped_explicitly():
    expected = [
        "programs/ian-agency/contexts/samlino/seo-agent-playground/AI-visibility/ARCHIVE-MAP.md",
        "programs/ian-agency/contexts/samlino/seo-agent-playground/seo-auditor/ARCHIVE-MAP.md",
        "programs/ian-agency/contexts/samlino/seo-agent-playground/samlino-mind-map/ARCHIVE-MAP.md",
    ]
    for rel in expected:
        assert (PROJECT_ROOT / rel).exists(), rel


def test_excluded_payload_noise_is_absent():
    forbidden = [
        "programs/artisan/reporting.theartisan.dk/the-artisan-wp",
        "programs/artisan/the-artisan-wp/wp-content/uploads",
        "programs/artisan/the-artisan-wp/wp-content/plugins",
        "programs/ian-agency/contexts/samlino/seo-agent-playground/AI-visibility/AI-Visibility copy",
    ]
    for rel in forbidden:
        assert not (PROJECT_ROOT / rel).exists(), rel


def test_nested_repo_and_cache_dirs_are_absent():
    for name in [".git", "node_modules", "venv", ".venv", "__pycache__", ".pytest_cache"]:
        matches = list((PROJECT_ROOT / "programs").rglob(name))
        assert not matches, f"found {name}: {matches[:5]}"
