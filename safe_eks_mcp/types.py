from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, NotRequired, TypeAlias

from typing_extensions import TypedDict

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
OpsMode: TypeAlias = Literal["readonly", "control"]
PolicyIntent: TypeAlias = Literal["readonly", "confirmed_control"]
PlanKind: TypeAlias = Literal["kubectl_apply", "helm_upgrade"]
CliCommand: TypeAlias = Literal["aws", "kubectl", "helm"]
ToolStatus: TypeAlias = Literal["ok", "blocked", "failed"]


class CommandResultJson(TypedDict):
    command: str
    args: list[str]
    exitCode: int
    stdout: str
    stderr: str
    timedOut: bool


class ChangePlanJson(TypedDict):
    kind: PlanKind
    command: CliCommand
    args: list[str]
    confirmationHash: str
    confirmationToken: str
    warnings: list[str]


class ToolPayloadJson(TypedDict):
    status: ToolStatus
    result: NotRequired[CommandResultJson]
    plan: NotRequired[ChangePlanJson]
    reason: NotRequired[str]


@dataclass(frozen=True, slots=True)
class RuntimeConfig:
    mode: OpsMode
    command_timeout_ms: int
    max_output_bytes: int


@dataclass(frozen=True, slots=True)
class CommandResult:
    command: str
    args: tuple[str, ...]
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool


@dataclass(frozen=True, slots=True)
class ChangePlan:
    kind: PlanKind
    command: CliCommand
    args: tuple[str, ...]
    confirmation_hash: str
    confirmation_token: str
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ToolPayload:
    status: ToolStatus
    result: CommandResult | None = None
    plan: ChangePlan | None = None
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class CliInvocation:
    command: CliCommand
    args: tuple[str, ...]
    intent: PolicyIntent = "readonly"
