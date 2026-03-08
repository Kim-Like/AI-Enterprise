from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path("/Users/IAn/Agent/AI-Enterprise")
CANONICAL = [
    "soul.md",
    "user.md",
    "agents.md",
    "skills.md",
    "tools.md",
    "heartbeat.md",
    "ARCHITECTURE.md",
    "memory.md",
]


def _assert_canonical_packet(path: Path):
    missing = [name for name in CANONICAL if not (path / name).exists()]
    assert not missing, f"{path} missing {missing}"


def test_core_agents_have_complete_packets():
    _assert_canonical_packet(PROJECT_ROOT / "agents" / "IAn")
    _assert_canonical_packet(PROJECT_ROOT / "agents" / "Engineer")


def test_program_masters_exist_in_domain_scoped_locations():
    expected = {
        "platform/ian-master",
        "artisan/artisan-master",
        "lavprishjemmeside/lavprishjemmeside-master",
        "samlino/samlino-master",
        "baltzer/baltzer-master",
        "personal-assistant/personal-assistant-master",
    }
    for rel in expected:
        path = PROJECT_ROOT / "agents" / rel
        assert path.exists(), rel
        _assert_canonical_packet(path)


def test_specialist_task_packets_are_preserved():
    engineer_tasks = PROJECT_ROOT / "agents" / "Engineer" / "tasks"
    assert (engineer_tasks / "platform-reliability-task").exists()
    assert (engineer_tasks / "integration-architecture-task").exists()
    assert (engineer_tasks / "data-observability-task").exists()

    samlino_tasks = PROJECT_ROOT / "agents" / "samlino" / "samlino-master" / "tasks"
    assert (samlino_tasks / "samlino-schema-generator-task").exists()
    assert (samlino_tasks / "samlino-seo-auditor-task").exists()
    assert (samlino_tasks / "samlino-prototyper-task").exists()


def test_historical_or_legacy_nodes_are_not_promoted():
    assert not (PROJECT_ROOT / "agents" / "Orchestration").exists()
    assert not (PROJECT_ROOT / "agents" / "samlino" / "ian").exists()
