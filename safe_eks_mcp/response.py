from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel, ConfigDict

from .types import ChangePlan, ChangePlanJson, CommandResult, CommandResultJson, ToolPayload, ToolPayloadJson


class CommandResultModel(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    command: str
    args: list[str]
    exitCode: int
    stdout: str
    stderr: str
    timedOut: bool


class ChangePlanModel(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    kind: str
    command: str
    args: list[str]
    confirmationHash: str
    confirmationToken: str
    warnings: list[str]


class ToolPayloadModel(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    status: str
    result: CommandResultModel | None = None
    plan: ChangePlanModel | None = None
    reason: str | None = None


def payload_dict(payload: ToolPayload) -> ToolPayloadJson:
    data: ToolPayloadJson = {"status": payload.status}
    if payload.result is not None:
        data["result"] = command_result_dict(payload.result)
    if payload.plan is not None:
        data["plan"] = change_plan_dict(payload.plan)
    if payload.reason is not None:
        data["reason"] = payload.reason
    return data


def payload_model(payload: ToolPayloadJson) -> ToolPayloadModel:
    return ToolPayloadModel.model_validate(payload)


def to_camel(value: str) -> str:
    parts = value.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


def command_result_dict(result: CommandResult) -> CommandResultJson:
    return {
        "command": result.command,
        "args": list(result.args),
        "exitCode": result.exit_code,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "timedOut": result.timed_out,
    }


def change_plan_dict(plan: ChangePlan) -> ChangePlanJson:
    return {
        "kind": plan.kind,
        "command": plan.command,
        "args": list(plan.args),
        "confirmationHash": plan.confirmation_hash,
        "confirmationToken": plan.confirmation_token,
        "warnings": list(plan.warnings),
    }
