---
name: eks-monitoring
description: Investigate EKS workload health, events, logs, RBAC, and Helm release state using safe read-only MCP tools.
---

# EKS Monitoring

Use read-only kubectl and Helm tools to diagnose incidents without changing cluster state.

## Rules

- Require explicit `region` and `cluster` context before querying workloads.
- Start broad with `kubectl_get` and `kubectl_events`, then narrow to `kubectl_describe` and `kubectl_logs`.
- Keep log reads bounded with `tail` and `since`.
- Use `kubectl_auth_can_i` before recommending an operation that might be blocked by RBAC.
- Do not fetch Secret values or print credentials.

## Monitoring Tools

- `kubectl_get`
- `kubectl_describe`
- `kubectl_logs`
- `kubectl_events`
- `kubectl_auth_can_i`
- `helm_status`
- `helm_history`
