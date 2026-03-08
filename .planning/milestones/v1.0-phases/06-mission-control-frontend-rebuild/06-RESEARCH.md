---
phase: 6
slug: mission-control-frontend-rebuild
created: 2026-03-08
status: complete
---

# Phase 6 Research

## Brownfield Facts That Matter

- The source control-plane frontend uses React 18, TypeScript, Vite, React Router, and Tailwind.
- The source route map currently includes `/`, `/programs`, `/orchestration-center`, `/agents/configs`, `/report`, `/agents/:id/chat`, and `/agents/:id/activity`.
- The source build writes compiled assets into `backend/static/ui`, which the codebase map identified as a drift risk because generated output sits beside source.
- The codebase concerns doc identifies frontend test coverage as a major gap and explicitly calls out browser-side secret storage in the source UI.

## Clean-Build Implications

- The clean target should not copy `frontend/` from the source repo.
- The clean target should not build into a backend-owned static folder during the initial rebuild phase.
- The clean target should treat the Phase 5 backend APIs as the canonical contract, not legacy source fetch helpers.
- The clean target should introduce frontend tests during the rebuild instead of repeating the brownfield “build-only” posture.

## Route Translation Decision

Source route:

- `/orchestration-center`

Clean route:

- `/orchestration`

Rationale:

- The PRD defines `/orchestration`
- The clean backend now exposes normalized `/api/control-ui/orchestration/*` endpoints
- The old route name should survive only as a redirect alias

## Styling Approach Decision

Recommended clean styling model:

- CSS variable tokens in `src/styles/tokens.css`
- purpose-built component CSS in one app stylesheet
- no dependency on the brownfield Tailwind implementation

Rationale:

- The clean file structure in the PRD centers `tokens.css`
- The desired visual language is highly specific and easier to control with authored CSS than utility carryover
- Removing Tailwind from the new UI reduces hidden coupling to legacy build assumptions

## Font Loading Decision

Recommended packages:

- `@fontsource/ibm-plex-mono`
- `@fontsource/dm-sans`

Rationale:

- Runtime font hosting becomes local and deterministic
- The PRD typography contract is explicit
- Avoids depending on third-party CDN delivery for a mission-control UI

## State And Data Strategy

Recommended frontend state model:

- React Router for navigation
- plain React state/hooks for page data
- one shared API client for same-origin calls
- one in-memory auth context for operator headers

Avoid:

- `localStorage`
- global client-side secret persistence
- unnecessary state libraries

Rationale:

- The app is operational, not consumer-scale
- The Phase 5 backend already exposes DTO-friendly JSON payloads
- In-memory auth honors the Phase 4 security direction while still letting a single operator use the UI

## Testing Strategy

Recommended frontend verification stack:

- Vitest
- React Testing Library
- `npm run build`

Rationale:

- The brownfield map flagged frontend testing as a critical gap
- Route-shell rendering and auth behavior are cheap to lock down with component tests
- Build verification alone is insufficient for this phase

## Phase Split Recommendation

Plan `06-01`:

- establish the frontend toolchain
- implement tokens, typography, shell primitives, route skeletons, and smoke tests

Plan `06-02`:

- implement full page surfaces
- wire live API calls
- add route-level interaction tests

This split keeps the shell/design system independently verifiable before live data wiring begins.
