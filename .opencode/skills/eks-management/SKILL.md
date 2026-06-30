---
name: eks-management
description: Safely inspect Amazon EKS clusters, node groups, add-ons, kubeconfig dry-runs, Kubernetes resources, and Helm releases through the readonly safe-eks MCP server.
---

# EKS Management

Use the `safe-eks` MCP tools for EKS inventory and read-only administration.

## Rules

- Run this skill inside the `hermes-closed-loop` workflow for non-trivial requests: observe, plan, act, verify, reflect, then update skills only with verified reusable lessons.
- Start in readonly mode. Do not request credentials, kubeconfig contents, or secrets.
- Always ask for `region` and `cluster` when a tool touches a specific EKS cluster.
- Prefer AWS tools for EKS control-plane inventory and kubectl/helm tools for workload state.
- Use `eks_generate_kubeconfig_dry_run` only to inspect generated kubeconfig output; do not write kubeconfig files.
- After verified management work, update this skill only for durable inventory or context-selection lessons. Put unverified lessons in `.opencode/learning/skill-backlog.md`.

## Useful Tools

- `aws_eks_list_clusters`
- `aws_eks_describe_cluster`
- `aws_eks_list_nodegroups`
- `aws_eks_describe_nodegroup`
- `aws_eks_list_addons`
- `aws_eks_describe_addon`
- `kubectl_get`
- `kubectl_describe`
- `helm_list`
- `helm_status`
- `helm_history`
