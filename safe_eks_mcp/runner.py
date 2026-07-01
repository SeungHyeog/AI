from __future__ import annotations

from .exec import execute
from .policy import Deny, enforce_policy
from .response import payload_dict
from .types import CliInvocation, RuntimeConfig, ToolPayload, ToolPayloadJson


def command_tool(config: RuntimeConfig, invocation: CliInvocation) -> ToolPayloadJson:
    decision = enforce_policy(invocation)
    if isinstance(decision, Deny):
        return payload_dict(ToolPayload(status="blocked", reason=decision.reason))
    result = execute(invocation.command, invocation.args, config)
    return payload_dict(ToolPayload(status="ok" if result.exit_code == 0 else "failed", result=result))
