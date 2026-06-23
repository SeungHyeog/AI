---
description: Triage an EKS incident with read-only evidence gathering.
---

Use the `eks-monitoring` skill.

Ask for `region`, `cluster`, namespace, and the affected workload or symptom. Gather evidence in this order:

1. `kubectl_get` for pods and deployments in the namespace
2. `kubectl_events` scoped to the namespace
3. `kubectl_describe` for affected pods, deployments, services, or ingress objects
4. `kubectl_logs` with a bounded `tail` for affected pods
5. `helm_status` and `helm_history` if a Helm release owns the workload
6. `kubectl_auth_can_i` for any operation you may recommend

Report probable cause, blast radius, immediate safe checks, and any control action that should be planned separately. Do not execute control actions in this incident command.
