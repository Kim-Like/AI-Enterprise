from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path("/Users/IAn/Agent/AI-Enterprise")


def test_phase_8_contract_artifacts_exist():
    assert (PROJECT_ROOT / "docs" / "cpanel-runtime-contract.md").exists()
    assert (PROJECT_ROOT / "scripts" / "_cpanel_common.sh").exists()
    assert (PROJECT_ROOT / "scripts" / "check_remote_config_contract.sh").exists()
    assert (PROJECT_ROOT / "scripts" / "verify_remote_portfolio.sh").exists()


def test_phase_8_env_template_excludes_removed_datastore_secrets():
    text = (PROJECT_ROOT / ".env.example").read_text()
    removed_prefixes = ("SUPA" + "BASE_", "HOSTED" + "_DB_")
    assert removed_prefixes[0] not in text
    assert removed_prefixes[1] not in text


def test_validation_script_runs_phase_8_remote_checks():
    text = (PROJECT_ROOT / "scripts" / "validate_ai_enterprise.sh").read_text()
    assert "check_remote_config_contract.sh" in text
    assert "verify_remote_portfolio.sh" in text
