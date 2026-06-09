# KubePilot AI

KubePilot AI is an AI DevOps Copilot for Kubernetes operations. It is designed to review deployment risk, summarize incidents, and prepare rollback guidance by combining an AI backend, MCP servers, and reusable operational skills.

This repository follows the direction in `PROJECT_DIRECTION.md`.

## Current Scope

- FastAPI backend skeleton with health and chat endpoints
- Markdown-based skills for incident triage and deployment risk review
- Jenkins pipeline draft for lint, test, image build, scan, and Helm validation
- Docker and Helm templates for the backend service
- Placeholder documentation for MCP integrations

## Quick Start

```bash
cd apps/backend
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Health check:

```bash
curl http://localhost:8000/healthz
```

Chat API:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"production에서 checkout-api가 느려졌어. 원인 분석해줘."}'
```

## Repository Layout

```text
apps/backend/        FastAPI backend
mcp-servers/         MCP server placeholders
skills/              Operational skill definitions
docs/                Architecture and implementation notes
deploy/helm/         Helm charts
observability/       Dashboard and alert placeholders
```

## MVP Principle

The MVP proposes operational actions but does not execute production-impacting commands automatically. Rollback, redeploy, scaling, and similar actions require explicit human approval.
