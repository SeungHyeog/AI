# Architecture

KubePilot AI combines a FastAPI backend, an LLM workflow, Markdown skills, and MCP servers.

The backend receives a user request, selects a skill, gathers evidence through MCP servers, and returns a grounded analysis. The MVP keeps command execution disabled by default and only suggests operational commands.

Primary integrations:

- Kubernetes for workload and event state
- Jenkins for CI/CD history and build logs
- Grafana and Prometheus for observability evidence
- GitHub for PR diff and release context
