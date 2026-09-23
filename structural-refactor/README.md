# structural-refactor skill

A research-backed coding-agent skill for finding and repairing structural degradation without equating "clean" with "more files".

## Modes

- **Audit:** read-only hotspot detection + semantic segmentation plan.
- **Refactor:** explicit, behavior-preserving implementation in verified microsteps.

## Install

Use the `structural-refactor/` directory as a skill directory. For Codex repository scope, place it under `.codex/skills/structural-refactor/`; for user scope, use `~/.codex/skills/structural-refactor/`.

The skill is intentionally portable and does not require its helper scripts. Scripts only provide deterministic triage signals; the semantic decision remains with the agent.
