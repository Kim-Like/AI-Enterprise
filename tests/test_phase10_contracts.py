from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from api.system.autonomy_service import build_provisioning_preflight_payload, load_repository_contracts


PROJECT_ROOT = Path("/Users/IAn/Agent/AI-Enterprise")


def test_phase_10_topology_manifest_carries_governed_provisioning_metadata():
    topology = json.loads((PROJECT_ROOT / "ops" / "repository-topology.json").read_text())
    assert topology["version"] == 2
    assert topology["policy"]["autonomy_rollout_stage"] == "wave1_preflight_only"

    repo_contracts = load_repository_contracts(PROJECT_ROOT)
    assert {repo["id"] for repo in repo_contracts} == {
        "ai-enterprise",
        "lavprishjemmeside.dk",
        "ljdesignstudio.dk",
        "reporting.theartisan.dk",
    }

    for repo in repo_contracts:
        primary_remote = repo["primary_remote"]
        autonomy = repo["autonomy"]
        assert primary_remote["provider"] == "github"
        assert primary_remote["namespace"] == "Kim-Like"
        assert primary_remote["credential_ref"] == "GITHUB_AUTONOMY_TOKEN"
        assert primary_remote["create_if_missing"] is True
        assert autonomy["scope"] == "governed_remote_provisioning"
        assert autonomy["allowed_modes"] == ["dry_run"]
        assert autonomy["wave"] == 1
        assert autonomy["preflight_only"] is True


def test_phase_10_topology_docs_preserve_single_source_of_truth():
    autonomy_doc = (PROJECT_ROOT / "docs" / "autonomy-provisioning.md").read_text()
    governance_doc = (PROJECT_ROOT / "docs" / "repository-governance.md").read_text()
    infrastructure_doc = (PROJECT_ROOT / "docs" / "infrastructure-topology.md").read_text()

    assert "only desired-state inventory" in autonomy_doc
    assert "No second provisioning YAML, JSON, or database inventory is allowed." in autonomy_doc
    assert "must read from `ops/repository-topology.json`" in governance_doc
    assert "manifest remains the canonical desired-state contract" in infrastructure_doc


def test_phase_10_topology_validation_script_accepts_wave1_metadata():
    env = os.environ.copy()
    env["GIT_GOVERNANCE_STRICT"] = "0"
    result = subprocess.run(
        ["bash", str(PROJECT_ROOT / "scripts" / "validate_git_governance.sh")],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "provisioning_contract_ok=ai-enterprise" in result.stdout
    assert "git_governance=ok" in result.stdout


def test_phase_10_provisioning_dry_run_reuses_bootstrap_preflight(monkeypatch):
    monkeypatch.setenv("GITHUB_AUTONOMY_TOKEN", "github-service-token")
    payload = build_provisioning_preflight_payload(
        project_root=PROJECT_ROOT,
        repo_ids=["ai-enterprise"],
    )

    assert payload["status"] == "ok"
    assert payload["dry_run"] is True
    assert payload["preflight_only"] is True
    assert payload["live_writes_blocked"] is True

    repo = payload["repositories"][0]
    assert repo["repo_id"] == "ai-enterprise"
    assert repo["credential_present"] is True
    assert repo["status"] == "preflight_ready"
    assert "preflight_provider_create_if_missing" in repo["planned_actions"]
    assert "bootstrap_primary_remote.sh" in repo["bootstrap_command"]


def test_phase_10_provisioning_wrapper_emits_json_report(monkeypatch):
    monkeypatch.setenv("GITHUB_AUTONOMY_TOKEN", "github-service-token")
    result = subprocess.run(
        [
            "bash",
            str(PROJECT_ROOT / "scripts" / "provision_governed_remote.sh"),
            "--repo-id",
            "ai-enterprise",
            "--mode",
            "dry_run",
            "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["dry_run"] is True
    assert payload["repositories"][0]["repo_id"] == "ai-enterprise"


def test_phase_10_provisioning_flags_missing_provider_credential(monkeypatch):
    monkeypatch.delenv("GITHUB_AUTONOMY_TOKEN", raising=False)
    payload = build_provisioning_preflight_payload(
        project_root=PROJECT_ROOT,
        repo_ids=["ai-enterprise"],
    )
    repo = payload["repositories"][0]
    assert repo["status"] == "blocked"
    assert "missing_provider_credential" in repo["validation_errors"]


def test_phase_10_provisioning_rejects_live_mode_before_audit_ready():
    result = subprocess.run(
        [
            "bash",
            str(PROJECT_ROOT / "scripts" / "provision_governed_remote.sh"),
            "--repo-id",
            "ai-enterprise",
            "--mode",
            "provision",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "preflight only" in (result.stderr + result.stdout).lower()
