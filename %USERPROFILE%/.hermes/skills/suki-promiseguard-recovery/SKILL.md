---
name: suki-promiseguard-recovery
description: Recover delivery-related customer complaints with evidence-backed actions and promise safety checks.
---

# Suki PromiseGuard recovery workflow

## When to use this skill

Use this when operations or customer support asks which delivery complaints should be recovered first, and how to respond without making unsupported promises.

## Tools this skill uses

1. `mcp_suki_find_recovery_cases` — shortlist and rank open/pending delivery cases.
2. `mcp_suki_prepare_recovery_plan` — gather evidence, propose safe action, and run Promise Check.
3. `mcp_suki_publish_recovery_card` — render GUI-ready evidence card payload.
4. `mcp_suki_apply_recovery_action` — apply approved assignment/escalation transaction.
5. `mcp_suki_get_recovery_result` — read back persisted change + audit trail.

## Procedure

1. Call `find_recovery_cases` with branch (default `Cubao`) and bounded limit.
2. Prioritize by urgency (priority), unanswered status, and age.
3. For chosen ticket, call `prepare_recovery_plan` and inspect:
   - what happened,
   - ticket → order → delivery evidence,
   - uncertainties,
   - Promise Check safe vs blocked items.
4. Call `publish_recovery_card` for a compact evidence card.
5. Ask approval before mutation.
6. On approval, call `apply_recovery_action(ticket_id, owner_id, plan_token_value)`.
7. Immediately call `get_recovery_result(action_id)` (or use returned result) and present verified before/after state.

## Output format

- Headline with one top case recommendation.
- Evidence card with Promise Check.
- Verified result card must include:
  - previous/current owner and status,
  - action ID,
  - response draft,
  - “Draft only—not sent”,
  - “Assigned—not resolved”.

## Pitfalls

- Treat staffing gaps as context, not proven causality.
- Never invent ETA, refund authorization, or delivery outcome.
- Exclude or flag invalid chronology (ticket before order).
- Require approval before write.
- Duplicate approvals must return existing action result, not create duplicates.
- If plan is stale, refresh plan before re-applying.
