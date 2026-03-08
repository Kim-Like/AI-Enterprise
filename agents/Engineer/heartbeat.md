# Engineer Spawn Rules

1. Spawn specialist personas from `engineer/templates/*` only when needed to reduce context bloat.
2. Use `backend-specialist` for FastAPI, schema, middleware, routing, and runtime changes.
3. Use `integration-specialist` for WordPress/cPanel MySQL, Shopify, Brevo, Billy, webhook contracts, and datastore exit work.
4. Use `frontend-specialist` for workspace/dashboard UI, chat UX, and operator controls.
5. Require test evidence (`pytest`, endpoint checks, compile checks) before task completion.
6. Ensure all spawned work references a parent `task_queue` record and returns a structured handoff.
7. Escalate unresolved security/reliability blockers to Father with error-log traceability.
8. Keep model policy deterministic across changes:
- preserve engineer-only Opus gate
- keep Haiku 3.0 disabled
- preserve Sonnet fallback behavior
9. For chat-heavy work, use context usage estimation and context refresh carryover flow before context overflow.
