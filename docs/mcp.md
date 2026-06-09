# MCP

MCP servers are the evidence collection layer for KubePilot AI.

Initial MVP servers:

- `kubernetes-mcp`
- `jenkins-mcp`
- `grafana-mcp`

The first implementation should favor read-only operations. Any write operation such as rollback, scale, redeploy, or traffic changes must be protected by explicit human approval.
