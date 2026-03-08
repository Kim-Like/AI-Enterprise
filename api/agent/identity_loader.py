"""Agent identity loader."""
from pathlib import Path
from typing import Dict, Optional

IDENTITY_FILES = [
    "soul.md",
    "user.md",
    "agents.md",
    "skills.md",
    "tools.md",
    "heartbeat.md",
    "ARCHITECTURE.md",
    "memory.md",
]


def load_identity(agent_dir: str) -> Dict[str, str]:
    agent_path = Path(agent_dir)
    if not agent_path.is_dir():
        raise FileNotFoundError(f"Agent directory not found: {agent_dir}")

    docs: Dict[str, str] = {}
    for filename in IDENTITY_FILES:
        file_path = agent_path / filename
        if file_path.exists():
            docs[filename] = file_path.read_text().strip()
    return docs


def build_system_prompt(identity_docs: Dict[str, str], skills_text: Optional[str] = None) -> str:
    parts = []
    for filename in IDENTITY_FILES:
        if filename in identity_docs:
            parts.append(f"--- {filename} ---\n{identity_docs[filename]}")
    if skills_text:
        parts.append(f"--- SKILLS ---\n{skills_text}")
    return "\n\n".join(parts)
