from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


PROJECT_ROOT = Path("/Users/IAn/Agent/AI-Enterprise")


def test_phase_9_contract_artifacts_exist():
    expected = [
        PROJECT_ROOT / "docs" / "infrastructure-topology.md",
        PROJECT_ROOT / "docs" / "repository-governance.md",
        PROJECT_ROOT / "docs" / "deployment-provenance.md",
        PROJECT_ROOT / "ops" / "repository-topology.json",
        PROJECT_ROOT / "scripts" / "_git_governance_common.sh",
        PROJECT_ROOT / "scripts" / "bootstrap_primary_remote.sh",
        PROJECT_ROOT / "scripts" / "validate_git_governance.sh",
    ]
    for path in expected:
        assert path.exists(), path


def test_env_template_exposes_git_governance_variables():
    text = (PROJECT_ROOT / ".env.example").read_text()
    for key in [
        "AI_ENTERPRISE_PRIMARY_GIT_REMOTE",
        "AI_ENTERPRISE_GIT_MIRROR_REMOTE",
        "LAVPRISHJEMMESIDE_PRIMARY_GIT_REMOTE",
        "LJDESIGNSTUDIO_PRIMARY_GIT_REMOTE",
        "ARTISAN_REPORTING_PRIMARY_GIT_REMOTE",
        "GIT_GOVERNANCE_STRICT",
    ]:
        assert key in text


def test_repository_topology_manifest_is_complete():
    data = json.loads((PROJECT_ROOT / "ops" / "repository-topology.json").read_text())
    assert data["policy"]["code_source_of_truth"] == "git"
    assert data["policy"]["no_nested_repos"] is True
    assert {repo["classification"] for repo in data["repositories"]} == {"main", "independent"}
    repo_ids = {repo["id"] for repo in data["repositories"]}
    assert repo_ids == {
        "ai-enterprise",
        "lavprishjemmeside.dk",
        "ljdesignstudio.dk",
        "reporting.theartisan.dk",
    }
    surface_rows = data["surfaces"]
    surface_ids = {surface["id"] for surface in surface_rows}
    assert len(surface_rows) == 34
    assert {"ian-control-plane", "lavprishjemmeside-cms", "ian-mission-control"} <= surface_ids
    assert {surface["classification"] for surface in data["surfaces"]} == {
        "main",
        "independent",
        "embedded",
        "archive",
    }


def test_validate_script_is_wired_into_canonical_validation():
    text = (PROJECT_ROOT / "scripts" / "validate_ai_enterprise.sh").read_text()
    assert "validate_git_governance.sh" in text


def test_validate_git_governance_runs_in_non_strict_mode():
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
    assert "git_governance=ok" in result.stdout


def test_bootstrap_primary_remote_initializes_repo_and_origin(tmp_path: Path):
    repo_path = tmp_path / "repo"
    remote_url = "ssh://git@example.test/srv/git/example.git"
    result = subprocess.run(
        [
          "bash",
          str(PROJECT_ROOT / "scripts" / "bootstrap_primary_remote.sh"),
          "--repo-path",
          str(repo_path),
          "--primary-remote",
          remote_url,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert (repo_path / ".git").exists()

    remote_result = subprocess.run(
        ["git", "-C", str(repo_path), "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert remote_result.stdout.strip() == remote_url
