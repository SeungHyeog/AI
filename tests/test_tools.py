from __future__ import annotations

from pathlib import Path

import pytest

from safe_eks_mcp.aws_tools import aws_eks_list_clusters
from safe_eks_mcp.control_tools import apply_helm_upgrade_confirmed, apply_kubectl_apply_confirmed, plan_kubectl_apply
from safe_eks_mcp.helm_tools import helm_template
from safe_eks_mcp.kubectl_tools import kubectl_get
from safe_eks_mcp.types import ChangePlanJson, CommandResultJson, RuntimeConfig, ToolPayloadJson
from safe_eks_mcp.validation import InvalidInputError

from .conftest import read_log


def readonly_config() -> RuntimeConfig:
    return RuntimeConfig(mode="readonly", command_timeout_ms=5_000, max_output_bytes=20_000)


def result_from(payload: ToolPayloadJson) -> CommandResultJson:
    result = payload.get("result")
    assert result is not None
    return result


def plan_from(payload: ToolPayloadJson) -> ChangePlanJson:
    plan = payload.get("plan")
    assert plan is not None
    return plan


def reason_from(payload: ToolPayloadJson) -> str:
    reason = payload.get("reason")
    assert reason is not None
    return reason


def test_aws_list_clusters_invokes_fake_cli_and_redacts_output(fake_cli: Path) -> None:
    payload = aws_eks_list_clusters(readonly_config(), "us-east-1")
    result = result_from(payload)

    assert payload["status"] == "ok"
    assert result["command"] == "aws"
    assert result["args"] == ["eks", "list-clusters", "--region", "us-east-1", "--output", "json"]
    assert "[REDACTED]" in result["stdout"]
    assert len(read_log(fake_cli)) == 1


def test_secret_resource_is_blocked_before_cli_execution(fake_cli: Path) -> None:
    payload = kubectl_get(readonly_config(), "us-east-1", "dev", "secrets", namespace="default")

    assert payload["status"] == "blocked"
    assert "Secret" in reason_from(payload)
    assert read_log(fake_cli) == []


def test_kubectl_apply_plan_uses_client_dry_run(fake_cli: Path) -> None:
    _ = fake_cli
    payload = plan_kubectl_apply(readonly_config(), "us-east-1", "dev", "./deploy.yaml", "default")
    result = result_from(payload)
    plan = plan_from(payload)

    assert payload["status"] == "ok"
    assert "--dry-run=client" in result["args"]
    assert "--dry-run=server" not in result["args"]
    assert "does not contact the cluster" in " ".join(plan["warnings"])


def test_readonly_apply_is_blocked_after_plan(fake_cli: Path) -> None:
    plan = plan_from(plan_kubectl_apply(readonly_config(), "us-east-1", "dev", "./deploy.yaml", "default"))
    payload = apply_kubectl_apply_confirmed(
        readonly_config(),
        "us-east-1",
        "dev",
        "./deploy.yaml",
        plan["confirmationHash"],
        plan["confirmationToken"],
        "default",
    )

    assert payload["status"] == "blocked"
    assert "EKS_OPS_MODE=control" in reason_from(payload)
    assert len(read_log(fake_cli)) == 1


def test_bad_helm_confirmation_is_blocked_before_execution(fake_cli: Path) -> None:
    control_config = RuntimeConfig(mode="control", command_timeout_ms=5_000, max_output_bytes=20_000)
    payload = apply_helm_upgrade_confirmed(
        control_config,
        "us-east-1",
        "dev",
        "api",
        "./chart",
        "0" * 64,
        "confirm:wrong-token-value",
        "default",
    )

    assert payload["status"] == "blocked"
    assert "did not match" in reason_from(payload)
    assert read_log(fake_cli) == []


def test_raw_secret_path_injection_is_rejected(fake_cli: Path) -> None:
    with pytest.raises(InvalidInputError):
        _ = kubectl_get(readonly_config(), "us-east-1", "dev", "--raw", "/api/v1/namespaces/default/secrets/foo")
    assert read_log(fake_cli) == []


def test_helm_leading_dash_release_is_rejected(fake_cli: Path) -> None:
    with pytest.raises(InvalidInputError):
        _ = helm_template(readonly_config(), "us-east-1", "dev", "--kube-context", "./chart", "default")
    assert read_log(fake_cli) == []


def test_normal_kubectl_get_pods_executes_fake_cli(fake_cli: Path) -> None:
    _ = fake_cli
    payload = kubectl_get(readonly_config(), "us-east-1", "dev", "pods", namespace="default")
    result = result_from(payload)

    assert payload["status"] == "ok"
    assert "pods" in result["args"]
