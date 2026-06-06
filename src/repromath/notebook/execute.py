"""Optional notebook execution helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import time

from nbclient.exceptions import CellExecutionError
from nbclient import NotebookClient
import nbformat


@dataclass(frozen=True)
class NotebookExecutionResult:
    attempted: bool
    passed: bool
    error: str | None = None
    runtime_seconds: float | None = None
    first_failing_cell_index: int | None = None
    error_name: str | None = None
    error_message: str | None = None


def execute_notebook(notebook: nbformat.NotebookNode, notebook_path: Path) -> NotebookExecutionResult:
    client = NotebookClient(
        notebook,
        timeout=120,
        kernel_name="python3",
        resources={"metadata": {"path": str(notebook_path.parent)}},
    )
    start = time.perf_counter()
    try:
        client.execute()
    except Exception as error:
        runtime_seconds = time.perf_counter() - start
        failing_cell = _first_error_output(notebook)
        error_name = _error_name(error, failing_cell)
        error_message = _error_message(error, failing_cell)
        return NotebookExecutionResult(
            attempted=True,
            passed=False,
            error=str(error),
            runtime_seconds=runtime_seconds,
            first_failing_cell_index=failing_cell[0] if failing_cell else None,
            error_name=error_name,
            error_message=error_message,
        )
    return NotebookExecutionResult(
        attempted=True,
        passed=True,
        runtime_seconds=time.perf_counter() - start,
    )


def _first_error_output(
    notebook: nbformat.NotebookNode,
) -> tuple[int, str | None, str | None] | None:
    for index, cell in enumerate(notebook.cells):
        if cell.cell_type != "code":
            continue
        for output in cell.get("outputs", []):
            if output.get("output_type") == "error":
                return (
                    index,
                    output.get("ename"),
                    output.get("evalue"),
                )
    return None


def _error_name(
    error: Exception,
    failing_cell: tuple[int, str | None, str | None] | None,
) -> str:
    if failing_cell and failing_cell[1]:
        return failing_cell[1]
    if isinstance(error, CellExecutionError):
        return error.ename
    return type(error).__name__


def _error_message(
    error: Exception,
    failing_cell: tuple[int, str | None, str | None] | None,
) -> str:
    if failing_cell and failing_cell[2]:
        return failing_cell[2]
    if isinstance(error, CellExecutionError):
        return error.evalue
    return str(error).splitlines()[0] if str(error) else type(error).__name__
