"""Simple artifact schema for repromath.toml provenance entries."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Artifact:
    id: str
    artifact_type: str
    output: str
    source: str | None = None
    role: str | None = None
    used_in: str | None = None
    diagnostics: list[str] = field(default_factory=list)

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "Artifact":
        diagnostics = data.get("diagnostics", [])
        if not isinstance(diagnostics, list):
            diagnostics = []
        return cls(
            id=str(data.get("id", "")),
            artifact_type=str(data.get("type", "")),
            output=str(data.get("output", "")),
            source=_optional_string(data.get("source")),
            role=_optional_string(data.get("role")),
            used_in=_optional_string(data.get("used_in")),
            diagnostics=[str(item) for item in diagnostics],
        )


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None

