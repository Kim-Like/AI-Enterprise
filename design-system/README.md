# Design System Workflow

This directory is the project-local source of truth for design-system output generated with `ui-ux-pro-max`.

## Installed Skill

- Shared skill location: `~/.codex/skills/ui-ux-pro-max`
- Search tool: `python3 ~/.codex/skills/ui-ux-pro-max/scripts/search.py`

## Required Workflow For AI-Enterprise

1. Run a design-system pass from the repo root.
2. Persist the approved global system into `design-system/MASTER.md`.
3. Add route-specific overrides under `design-system/pages/` only when a route intentionally deviates from the global system.
4. Follow the persisted system during implementation and review.

## Commands

### Global design-system pass

```bash
cd /Users/IAn/Agent/AI-Enterprise
python3 ~/.codex/skills/ui-ux-pro-max/scripts/search.py \
  "AI enterprise mission control dashboard operational tooling" \
  --design-system \
  --persist \
  -p "AI Enterprise"
```

### Route-specific override

```bash
cd /Users/IAn/Agent/AI-Enterprise
python3 ~/.codex/skills/ui-ux-pro-max/scripts/search.py \
  "AI enterprise orchestration control center run timeline operator workflow" \
  --design-system \
  --persist \
  -p "AI Enterprise" \
  --page "orchestration"
```

### React-specific implementation guidance

```bash
cd /Users/IAn/Agent/AI-Enterprise
python3 ~/.codex/skills/ui-ux-pro-max/scripts/search.py "dashboard layout dense information states" --stack react
python3 ~/.codex/skills/ui-ux-pro-max/scripts/search.py "keyboard focus reduced motion operator workflow" --domain ux
```

## AI-Enterprise Constraints

- Do not accept the skill's generic `html-tailwind` default as the implementation target.
- The canonical UI stack is React + TypeScript + authored CSS.
- Keep design choices aligned with the mission-control character already defined in `src/styles/tokens.css`.
- Use the skill to improve clarity, visual hierarchy, typography, palette discipline, and anti-pattern avoidance, not to replace repo-specific architecture.

## Expected Files

- `design-system/MASTER.md`
- `design-system/pages/<route>.md`
