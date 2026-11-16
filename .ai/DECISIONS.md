# Decisions

- 2026-11-16 | codex | Review PR14 in an isolated worktree to preserve the primary checkout.
- 2026-11-16 | codex | Regenerate license inventories after lock changes; original PR14 fails
  the inventory guard without that correction. No application changes were needed.
- 2026-11-16 | codex | Retain initial timing/socket failures and repeat checks sequentially
  with original settings; do not label transient failures green or weaken tests/timeouts.
- 2026-11-16 | codex | Keep handoff in `.ai/HANDOFF.md` per explicit owner instructions,
  overriding the handoff skill's temporary-directory default. No remote push for handoff.

- 2026-11-16 | codex | Owner approved publishing corrected PR14 work and hosted verification; preserve the existing PR via a fast-forward push, with no merge or policy changes.
