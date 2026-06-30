---
description: Run a Hermes-inspired closed learning loop for the current request.
---

Use the `hermes-closed-loop` skill for the whole request.

Follow this loop exactly:

1. Observe: restate the goal, inspect relevant files, and load/read applicable skills.
2. Plan: define verifiable steps and safety constraints.
3. Act: implement or investigate using the safest project-native tools.
4. Verify: run tests, builds, MCP dry-runs, or direct file checks as appropriate.
5. Reflect: identify reusable lessons and separate them from one-off facts.
6. Update skills: edit `.opencode/skills/*/SKILL.md` only for verified reusable lessons; otherwise append to `.opencode/learning/skill-backlog.md`.

For EKS work, also use the relevant `eks-management`, `eks-monitoring`, or `eks-control` skill. Do not run mutating EKS operations unless the user explicitly requests them and the confirmation-gated control workflow succeeds.
