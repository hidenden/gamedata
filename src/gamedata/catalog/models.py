"""JSON-compatible catalog records. No runtime or database dependencies."""

from typing import Any, TypedDict

SCHEMA_VERSION = 1


class Record(TypedDict, total=False):
    schema_version: int
    id: str
    kind: str
    summary: str
    columns: dict[str, Any]
    related: list[str]


def record(identifier: str, summary: str, **fields: Any) -> Record:
    return {
        "schema_version": SCHEMA_VERSION,
        "id": identifier,
        "kind": identifier.split(":", 1)[0],
        "summary": summary,
        **fields,
    }
