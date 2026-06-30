---
name: hermes-closed-loop
description: Use for every non-trivial project request to run a Hermes-inspired closed learning loop: observe, plan, act, verify, reflect, and update skills with reusable lessons.
---

# Hermes Closed Loop

Use this skill as the project operating loop. It adapts Hermes Agent's closed learning-loop principles to this OpenCode repo: learn from completed work, improve procedural skills during use, and preserve useful lessons across sessions without storing secrets or weakening safety controls.

## Core Loop

Run these phases for every non-trivial request:

1. **Observe**
   - Restate the user's goal in one concise line.
   - Inspect relevant project files before deciding.
   - Load domain skills that apply, especially `eks-management`, `eks-monitoring`, and `eks-control` for EKS work.
   - Check prior project knowledge: `README.md`, `.opencode/skills/*`, `.opencode/commands/*`, and `graphify-out/GRAPH_REPORT.md` when present.

2. **Plan**
   - Split work into verifiable steps.
   - Identify safety boundaries, required approvals, and external side effects.
   - For EKS control work, plan only; never apply until explicit user confirmation and the safe MCP control gates allow it.

3. **Act**
   - Execute the smallest safe change that satisfies the request.
   - Prefer project MCP tools over raw shell for EKS.
   - Keep generated caches and local tool environments out of commits unless the repo intentionally tracks them.

4. **Verify**
   - Run the narrowest meaningful verification first, then broaden when needed.
   - For this repo, default verification is `npm test`, `npm run typecheck`, and `npm run build` after code changes.
   - For OpenCode skill/command-only changes, validate frontmatter, file paths, and safety rules by reading the changed files.

5. **Reflect**
   - Identify reusable lessons from the request.
   - Separate durable procedural knowledge from one-off facts.
   - Do not record credentials, cluster secrets, tokens, private incident data, or user personal data.

6. **Update Skills**
   - If a lesson is verified, reusable, and project-specific, update the relevant `.opencode/skills/*/SKILL.md` in the same work cycle.
   - If the lesson is plausible but unverified, add it to `.opencode/learning/skill-backlog.md` instead of changing a skill.
   - Keep updates small: one new rule, pitfall, checklist item, or tool preference per lesson.

## Skill Update Gate

Only update a skill when all checks pass:

- The lesson came from a completed and verified task.
- The lesson would have changed future agent behavior for the better.
- The lesson is not already covered by an existing skill.
- The lesson is stable enough to reuse, not tied to a single transient error.
- The update does not expose secrets, credentials, internal cluster data, or private user context.
- The update does not weaken EKS read-only defaults or confirmation gates.

If any check fails, write a backlog item instead of editing the skill.

## Backlog Format

Use `.opencode/learning/skill-backlog.md` for lessons that need more evidence.

```markdown
## YYYY-MM-DD - Short lesson title

- Source request: short summary, no secrets
- Candidate skill: skill name or "new skill"
- Proposed update: exact rule/checklist/pitfall to add
- Evidence needed: what must be verified before promotion
```

## Reflection Format

At the end of significant work, include a short internal reflection in the final summary or work notes:

- **What changed:** user-visible result.
- **Verification:** commands or checks run.
- **Lesson:** reusable procedural insight, or "none".
- **Skill update:** updated skill path, backlog path, or "not needed".

## Guardrails

- Never run an autonomous infinite loop. Each loop handles the current user request and stops.
- Never update skills to justify a failed implementation. Fix the implementation first.
- Never store kubeconfig contents, Kubernetes Secrets, cloud credentials, access tokens, or incident-sensitive payloads.
- Never convert a one-off workaround into a rule without verification.
- Never bypass `safe-eks` MCP policy by using raw mutating shell commands.
- Never apply Kubernetes or Helm changes unless the user explicitly asks and the `eks-control` confirmation workflow succeeds.

## EKS-Specific Learning

When a task touches EKS:

- Management lessons go to `eks-management`.
- Incident/log/event lessons go to `eks-monitoring`.
- Apply/upgrade/rollback lessons go to `eks-control`.
- Safety lessons that span all EKS work go here and may be cross-referenced from the EKS skills.

## Verification Checklist

- [ ] Relevant files were inspected before action.
- [ ] Domain skills were loaded or their local skill files were read.
- [ ] Work was verified with commands or direct file checks.
- [ ] A reflection happened after verification.
- [ ] Skill updates were made only for verified reusable lessons.
- [ ] Unverified lessons were recorded in `.opencode/learning/skill-backlog.md`.
