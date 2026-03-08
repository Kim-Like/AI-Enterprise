# Lavprishjemmeside Master Spawn Rules

1. Route core platform objectives to `lph-ai-cms-task` first unless explicit override.
2. Route SEO reporting objectives to `lph-seo-dashboard-task`.
3. Route paid media reporting objectives to `lph-ads-dashboard-task`.
4. Route client revenue/retention objectives to `lph-subscription-ops-task`.
5. Escalate MySQL/cPanel infra incidents and cross-domain dependencies to Engineer.


## Warn-Only Orchestration Rules
6. Build a boundary plan from the matrix before specialist assignment.
7. When two boundaries overlap, select deterministic winner and emit `contract_warnings`.
8. Attach mission contract metadata (`mission_id`, `boundary_set_id`, `observability_tags`) to task context.
9. Preserve `correlation_id` across parent, child, result, and escalation flows.

## Claude Context Rules

1. Default master chat/runtime profile should remain `sonnet_46` unless policy allows another profile.
2. If model override is requested, verify policy outcome and record warnings/fallbacks.
3. Before long analysis turns, check `/api/chat/threads/{thread_id}/context-usage`.
4. If context status is `critical` or `over`, create a continuation via `/api/chat/threads/{thread_id}/context-refresh` and continue work there.
