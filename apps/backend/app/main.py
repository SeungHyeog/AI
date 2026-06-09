from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field


app = FastAPI(
    title="KubePilot AI Backend",
    description="AI DevOps Copilot backend for Kubernetes deployment and incident workflows.",
    version="0.1.0",
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    context: dict[str, Any] = Field(default_factory=dict)
    skill: str | None = None


class ChatResponse(BaseModel):
    answer: str
    selected_skill: str
    evidence_sources: list[str]
    recommended_actions: list[str]
    requires_approval: bool


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat")
def chat(request: ChatRequest) -> ChatResponse:
    selected_skill = request.skill or select_skill(request.message)

    return ChatResponse(
        answer=(
            "현재 MVP는 운영 데이터를 직접 조회하지 않습니다. "
            f"요청은 `{selected_skill}` 절차로 분석하고, MCP 연동 후 근거 데이터를 붙입니다."
        ),
        selected_skill=selected_skill,
        evidence_sources=[
            "kubernetes-mcp",
            "jenkins-mcp",
            "grafana-mcp",
        ],
        recommended_actions=[
            "관련 namespace, workload, 최근 event를 확인합니다.",
            "최근 Jenkins 배포 이력과 실패 로그를 대조합니다.",
            "Grafana/Prometheus 지표에서 latency, error rate, restart count를 확인합니다.",
        ],
        requires_approval=True,
    )


def select_skill(message: str) -> str:
    normalized = message.lower()
    if any(keyword in normalized for keyword in ["rollback", "롤백", "이전 버전"]):
        return "rollback-planner"
    if any(keyword in normalized for keyword in ["deploy", "배포", "pr"]):
        return "deployment-risk-review"
    return "incident-triage"
