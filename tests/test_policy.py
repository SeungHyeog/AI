from __future__ import annotations

from safe_eks_mcp.policy import Deny, enforce_policy
from safe_eks_mcp.types import CliInvocation


def test_mutating_commands_are_denied_in_readonly() -> None:
    assert isinstance(enforce_policy(CliInvocation("kubectl", ("--context", "dev", "delete", "pod", "api"))), Deny)
    assert isinstance(enforce_policy(CliInvocation("helm", ("upgrade", "api", "./chart"))), Deny)
    assert isinstance(enforce_policy(CliInvocation("aws", ("eks", "delete-cluster", "--name", "dev"))), Deny)


def test_raw_and_secret_references_are_denied() -> None:
    assert isinstance(
        enforce_policy(CliInvocation("kubectl", ("--context", "dev", "get", "--raw", "/api/v1/secrets/foo"))), Deny
    )
    assert isinstance(enforce_policy(CliInvocation("kubectl", ("--context", "dev", "get", "pods,secrets"))), Deny)
    assert isinstance(enforce_policy(CliInvocation("kubectl", ("--context", "dev", "describe", "sec", "foo"))), Deny)
