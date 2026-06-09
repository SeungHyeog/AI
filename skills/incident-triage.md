# incident-triage

## Purpose

Analyze a production or staging incident and produce likely causes, evidence, and next actions.

## Required MCP Tools

- `kubernetes-mcp`: pod, deployment, event, service, HPA lookup
- `jenkins-mcp`: recent deployment and build log lookup
- `grafana-mcp`: latency, error rate, restart count, and saturation metrics

## Check Order

1. Identify affected service, namespace, and time window.
2. Check pod status, deployment rollout status, and Kubernetes events.
3. Compare recent Jenkins deployment history with the incident start time.
4. Review Grafana/Prometheus metrics for latency, error rate, restart count, CPU, and memory.
5. Summarize the most likely cause with supporting evidence.

## Risk Criteria

- p95 latency or 5xx rate increased sharply after a deploy.
- Pod restart count or crash loop events increased.
- HPA scaling or resource saturation coincides with user impact.
- Logs show a repeated application error pattern.

## Result Format

```text
Most likely cause:

Evidence:
- ...

Recommended actions:
- ...

Approval required:
- Any rollback, redeploy, scale, or traffic change must be approved by a human.
```
