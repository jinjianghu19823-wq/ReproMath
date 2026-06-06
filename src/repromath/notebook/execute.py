"""Optional notebook execution helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from nbclient import NotebookClient
import nbformat


@dataclass(frozen=True)
class NotebookExecutionResult:
    attempted: bool
    passed: bool
    error: str | None = None


def execute_notebook(notebook: nbformat.NotebookNode, notebook_path: Path) -> NotebookExecutionResult:
    client = NotebookClient(
        notebook,
        timeout=120,
        kernel_name="python3",
        resources={"metadata": {"path": str(notebook_path.parent)}},
    )
    try:
        client.execute()
    except Exception as error:
        return NotebookExecutionResult(
            attempted=True,
            passed=False,
            error=str(error),
        )
    return NotebookExecutionResult(attempted=True, passed=True)
