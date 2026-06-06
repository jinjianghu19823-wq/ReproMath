"""Read ReproMath project metadata."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    import tomli as tomllib

from repromath.provenance.schema import Artifact


class ConfigError(Exception):
    """Raised when a ReproMath project config cannot be read."""


@dataclass(frozen=True)
class ProjectConfig:
    root: Path
    config_path: Path
    name: str
    project_type: str
    main_tex: str | None
    paths: dict[str, str]
    artifacts: list[Artifact]


def find_project_root(start: Path | None = None) -> Path | None:
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "repromath.toml").is_file():
            return candidate
    return None


def load_project_config(project_root: Path | None = None) -> ProjectConfig:
    root = project_root.resolve() if project_root is not None else find_project_root()
    if root is None:
        raise ConfigError("Could not find repromath.toml in the current directory or parents.")

    config_path = root / "repromath.toml"
    if not config_path.is_file():
        raise ConfigError(f"Project config not found: {config_path}")

    data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    project = _table(data, "project")
    paths = _table(data, "paths")
    artifacts = [
        Artifact.from_mapping(item)
        for item in data.get("artifacts", [])
        if isinstance(item, dict)
    ]

    return ProjectConfig(
        root=root,
        config_path=config_path,
        name=str(project.get("name", root.name)),
        project_type=str(project.get("type", "")),
        main_tex=_optional_string(project.get("main_tex")),
        paths={str(key): str(value) for key, value in paths.items()},
        artifacts=artifacts,
    )


def _table(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key, {})
    return value if isinstance(value, dict) else {}


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None

