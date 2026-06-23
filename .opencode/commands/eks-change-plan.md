---
description: Build a safe EKS change plan without applying it.
---

Use the `eks-control` skill.

Ask for the explicit `region`, `cluster`, namespace, and either manifest path or Helm release/chart details. Run exactly one planning tool:

- `plan_kubectl_apply` for Kubernetes manifests
- `plan_helm_upgrade` for Helm releases

Return the planned command, warnings, dry-run or rendered output summary, and the confirmation hash/token. Explain that apply remains disabled unless the MCP server is launched with `EKS_OPS_MODE=control` and the user explicitly confirms the exact plan.
