# rollback-planner

## Purpose

Prepare a rollback plan for a workload without executing the rollback automatically.

## Required MCP Tools

- `kubernetes-mcp`: current deployment revision and rollout status
- `jenkins-mcp`: rollback job and previous successful build lookup
- `grafana-mcp`: post-rollback verification metrics

## Check Order

1. Identify service, namespace, current version, and target stable version.
2. Confirm whether rollback should use Jenkins, Helm, or Kubernetes rollout history.
3. List exact commands or Jenkins job parameters as suggestions only.
4. Define post-rollback checks for latency, error rate, restart count, and traffic routing.

## Result Format

```text
Rollback target:

Suggested procedure:
- ...

Verification:
- ...

Approval required:
- The rollback must not run until a human explicitly approves it.
```
