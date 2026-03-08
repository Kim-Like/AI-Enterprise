# AI-Enterprise Local Operating Instructions

## Canonical Root

- Active project root: `/Users/IAn/Agent/AI-Enterprise`
- Active GSD root: `/Users/IAn/Agent/AI-Enterprise/.planning`
- Brownfield source reference: `/Users/IAn/Agent/IAn`

## Rules

- Keep all new planning, execution, and validation state inside `AI-Enterprise`.
- Treat `/Users/IAn/Agent/IAn` as source or archive material, not the live project root.
- Do not split future GSD work between both repos.

## Verification

- Preferred full validation command: `bash scripts/validate_ai_enterprise.sh`
- Autonomy-specific validation: `bash scripts/validate_autonomy.sh`

## Frontend Design Protocol

- Use `$ui-ux-pro-max` for non-trivial frontend design, design-system generation, and UI/UX anti-pattern review.
- For AI-Enterprise, do not stop at the skill's generic `html-tailwind` default. Follow design-system generation with stack-specific guidance for `react`.
- Persist design decisions in `design-system/MASTER.md` and `design-system/pages/<route>.md` once frontend design work starts.
- Keep AI-Enterprise visual decisions aligned with the existing mission-control language in `src/styles/tokens.css` unless the new phase explicitly redefines it.

## Notes

- The workspace-level instructions in `/Users/IAn/Agent/AGENTS.md` still apply.
- Legacy planning artifacts from the source-root era live at `/Users/IAn/Agent/IAn/.planning-source-archive`.
