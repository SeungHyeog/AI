---
description: Collect a readonly EKS status snapshot.
---

Use the `eks-management` and `eks-monitoring` skills.

Ask for `region` and `cluster` if they are missing. Then collect:

1. `aws_eks_describe_cluster`
2. `aws_eks_list_nodegroups`
3. `aws_eks_list_addons`
4. `kubectl_get` for nodes, pods, deployments, and services
5. `helm_list`
6. `kubectl_events` for recent warnings

Summarize health, degraded components, and recommended read-only follow-up checks. Do not run apply, upgrade, delete, scale, or restart operations.
