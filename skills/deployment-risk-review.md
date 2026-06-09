# deployment-risk-review

## Purpose

Review whether a PR or release is safe to deploy to staging or production.

## Required MCP Tools

- `github-mcp`: PR diff, commits, release notes
- `kubernetes-mcp`: current workload and namespace status
- `jenkins-mcp`: recent build and deployment status
- `grafana-mcp`: recent service health metrics

## Check Order

1. Inspect changed files, Dockerfile changes, Helm chart changes, and Kubernetes manifests.
2. Check recent Jenkins build and test results.
3. Check target namespace pod health and recent Kubernetes events.
4. Check latency, error rate, restart count, and resource saturation.
5. Identify canary, Istio, timeout, retry, and readiness/liveness probe risks.

## Risk Criteria

- Probe timeout is lower than current p95 latency.
- Canary traffic weight remains unexpectedly configured.
- Error rate is close to or above the service SLO.
- Deployment changes resource limits, replicas, routing, or secrets.

## Result Format

```text
Deployment recommendation:

Risks:
- ...

Recommended actions:
- ...

Approval required:
- Production deployment and rollback commands must be approved by a human.
```
