# Safe EKS MCP

Local TypeScript MCP server and OpenCode customization for safe Amazon EKS management, control planning, and monitoring.

The server is readonly by default. Read-only tools call local `aws`, `kubectl`, and `helm` binaries with explicit argv arrays, `shell: false`, isolated environment variables, command timeouts, bounded output, and credential redaction. Control tools require a plan-generated confirmation hash/token and are blocked unless the server is launched with `EKS_OPS_MODE=control`.

## Install and Build

```bash
npm install
npm run build
npm test
```

OpenCode is configured in `opencode.jsonc` to run:

```bash
node ./dist/index.js
```

with `EKS_OPS_MODE=readonly`.

## Safety Model

- No real AWS, kubeconfig, or cluster access is needed for tests.
- The server never stores or requests credentials.
- The command runner does not execute shell command strings.
- AWS/EKS tools require explicit `region`; cluster-scoped tools also require explicit `cluster`.
- Apply tools are disabled by default.
- Confirmation uses the exact command/argv hash from a plan response.

## Read-only Tools

- `aws_eks_list_clusters`
- `aws_eks_describe_cluster`
- `aws_eks_list_nodegroups`
- `aws_eks_describe_nodegroup`
- `aws_eks_list_addons`
- `aws_eks_describe_addon`
- `eks_generate_kubeconfig_dry_run`
- `kubectl_get`
- `kubectl_describe`
- `kubectl_logs`
- `kubectl_events`
- `kubectl_auth_can_i`
- `helm_list`
- `helm_status`
- `helm_history`
- `helm_template`
- `helm_lint`

## Control Workflows

Plan first:

- `plan_kubectl_apply`
- `plan_helm_upgrade`

Apply only after explicit approval and with the server launched in control mode:

- `apply_kubectl_apply_confirmed`
- `apply_helm_upgrade_confirmed`

The apply input must repeat the same operation details and include the matching `confirmationHash` and `confirmationToken` from the plan.

## OpenCode Additions

Skills:

- `.opencode/skills/eks-management/SKILL.md`
- `.opencode/skills/eks-control/SKILL.md`
- `.opencode/skills/eks-monitoring/SKILL.md`

Commands:

- `.opencode/commands/eks-status.md`
- `.opencode/commands/eks-change-plan.md`
- `.opencode/commands/eks-incident.md`

## Testing Approach

Vitest installs fake `aws`, `kubectl`, and `helm` binaries into a temporary directory and prepends that directory to `PATH`. Tests exercise MCP calls through an in-memory MCP client/server transport, so they do not require AWS credentials, kubeconfig, Helm repositories, or live clusters.
