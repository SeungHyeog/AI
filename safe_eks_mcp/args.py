from __future__ import annotations


def aws_region_args(region: str) -> tuple[str, ...]:
    return ("--region", region, "--output", "json")


def kubectl_context_args(cluster: str) -> tuple[str, ...]:
    return ("--context", cluster)


def namespace_args(namespace: str | None) -> tuple[str, ...]:
    return () if namespace is None else ("--namespace", namespace)


def key_value_set_args(values: dict[str, str | int | bool]) -> tuple[str, ...]:
    args: list[str] = []
    for key, value in values.items():
        args.extend(("--set", f"{key}={str(value).lower() if isinstance(value, bool) else value}"))
    return tuple(str(arg) for arg in args)
