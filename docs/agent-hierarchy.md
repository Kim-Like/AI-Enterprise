# Agent Hierarchy Duplication Map

## Core Mapping

| Source | Target | Notes |
|--------|--------|-------|
| `/Users/IAn/Agent/IAn/father` | `AI-Enterprise/agents/IAn` | canonical Father AI packet |
| `/Users/IAn/Agent/IAn/engineer` | `AI-Enterprise/agents/Engineer` | canonical Engineer packet plus existing task specialists |
| `/Users/IAn/Agent/IAn/masters/ian-master` | `AI-Enterprise/agents/platform/ian-master` | platform/domain master |
| `/Users/IAn/Agent/IAn/masters/artisan-master` | `AI-Enterprise/agents/artisan/artisan-master` | artisan domain master |
| `/Users/IAn/Agent/IAn/masters/lavprishjemmeside-master` | `AI-Enterprise/agents/lavprishjemmeside/lavprishjemmeside-master` | lavprishjemmeside domain master |
| `/Users/IAn/Agent/IAn/masters/samlino-master` | `AI-Enterprise/agents/samlino/samlino-master` | samlino domain master |
| `/Users/IAn/Agent/IAn/masters/baltzer-master` | `AI-Enterprise/agents/baltzer/baltzer-master` | baltzer domain master |
| `/Users/IAn/Agent/IAn/masters/personal-assistant-master` | `AI-Enterprise/agents/personal-assistant/personal-assistant-master` | personal-assistant domain master |

## Specialist Preservation

- Source specialist task packets remain under their owning master in the target tree.
- Engineer task specialists remain under `AI-Enterprise/agents/Engineer/tasks/`.
- Domain specialist packets remain under `AI-Enterprise/agents/<domain>/<master>/tasks/`.

## Excluded Nodes

- `/Users/IAn/Agent/IAn/masters/Orchestration`
  Reason: historical partial node, not part of the clean-build reference hierarchy.
- `/Users/IAn/Agent/IAn/programs/ian-agency/contexts/samlino/seo-agent-playground/ian`
  Reason: local legacy agent context, not a core hierarchy node.

## Canonical Packet Rule

- `IAn` and `Engineer` must each contain all 8 canonical files.
- Program masters preserve their full 8-file canonical packets.
- Specialists preserve their source task packet contents without inventing new canonical content in this phase.
