---
name: eks-control
description: Plan and execute tightly confirmation-gated EKS kubectl apply and Helm upgrade workflows through safe-eks MCP.
---

# EKS Control

Use control tools only for explicit user-approved changes.

## Rules

- Run this skill inside the `hermes-closed-loop` workflow so every change request ends with verification and safe reflection.
- Plan first with `plan_kubectl_apply` or `plan_helm_upgrade`.
- Read the dry-run or rendered manifest output before asking the user to approve.
- Apply tools are expected to be blocked unless the server is launched with `EKS_OPS_MODE=control`.
- Never invent a confirmation token. Use the exact `confirmationHash` and `confirmationToken` from the matching plan.
- Keep cluster, region, namespace, chart, release, values, and manifest path identical between plan and apply.
- After verified control work, update this skill only with reusable approval, rollback, or post-change verification lessons that preserve the confirmation gate.

## Change Tools

- `plan_kubectl_apply`
- `apply_kubectl_apply_confirmed`
- `plan_helm_upgrade`
- `apply_helm_upgrade_confirmed`
