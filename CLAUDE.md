# AI-Enterprise

Canonical project root:

- `/Users/IAn/Agent/AI-Enterprise`

Source brownfield reference:

- `/Users/IAn/Agent/IAn`

## Session Start Protocol

1. Read `.planning/STATE.md`
2. Read `.planning/ROADMAP.md`
3. Read `.planning/PROJECT.md`
4. Read the current phase packet in `.planning/phases/*` when executing planned work

## Project Boundary

- Treat this repo as the only active project root for planning, implementation, validation, and commits.
- Treat `/Users/IAn/Agent/IAn` as the brownfield source system and archive reference only.
- Do not create or update active GSD planning state under `/Users/IAn/Agent/IAn`.

## Execution Protocol

1. Implement active work inside this repo.
2. Preserve source traceability back to `/Users/IAn/Agent/IAn` where relevant.
3. Keep `.planning/` here as the canonical GSD state.
4. Run `bash scripts/validate_ai_enterprise.sh` before handoff for substantive changes.

## Path Discipline

- Create all new runtime, planning, and documentation files under this root unless explicitly archiving source material.
- If legacy planning artifacts are needed from the old source repo, reference `IAn/.planning-source-archive/` instead of recreating a second live `.planning/` tree.
