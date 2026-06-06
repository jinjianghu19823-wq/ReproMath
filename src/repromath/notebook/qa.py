"""Notebook QA checks for ReproMath."""

from __future__ import annotations

import copy
from dataclasses import asdict, dataclass
from pathlib import Path
import json
import re

import nbformat

from repromath.notebook.execute import NotebookExecutionResult, execute_notebook
from repromath.notebook.sections import REQUIRED_SECTIONS


@dataclass(frozen=True)
class NotebookQaResult:
    status: str
    notebook_file: str
    total_cells: int
    markdown_cells: int
    code_cells: int
    cells_with_outputs: int
    cells_with_execution_count: int
    sections_found: list[str]
    missing_sections: list[str]
    required_sections_passed: bool
    has_code_cells: bool
    random_seed_found: bool
    stale_output_detected: bool
    stale_output_warnings: list[str]
    execute_requested: bool
    execution_attempted: bool
    execution_passed: bool | None
    execution_runtime_seconds: float | None
    first_failing_cell_index: int | None
    execution_error_name: str | None
    execution_error_message: str | None
    execution_error: str | None
    report_markdown: str
    report_json: str


def run_notebook_qa(
    notebook_path: Path,
    execute: bool = False,
    cwd: Path | None = None,
) -> NotebookQaResult:
    notebook_path = notebook_path.expanduser()
    if not notebook_path.is_absolute():
        notebook_path = (cwd or Path.cwd()) / notebook_path
    notebook_path = notebook_path.resolve()

    if not notebook_path.is_file():
        raise FileNotFoundError(f"Notebook file not found: {notebook_path}")

    notebook = nbformat.read(notebook_path, as_version=4)
    cell_summary = _cell_summary(notebook)
    sections_found = _sections_found(notebook)
    missing_sections = [
        section for section in REQUIRED_SECTIONS if section not in sections_found
    ]
    required_sections_passed = not missing_sections
    code_sources = [
        cell.source for cell in notebook.cells if cell.cell_type == "code"
    ]
    has_code_cells = bool(code_sources)
    random_seed_found = _has_random_seed("\n".join(code_sources))
    stale_output_warnings = _stale_output_warnings(notebook)
    stale_output_detected = bool(stale_output_warnings)

    execution_result = (
        execute_notebook(copy.deepcopy(notebook), notebook_path)
        if execute
        else NotebookExecutionResult(attempted=False, passed=False)
    )

    status = _status(
        missing_sections=missing_sections,
        has_code_cells=has_code_cells,
        random_seed_found=random_seed_found,
        stale_output_detected=stale_output_detected,
        execute_requested=execute,
        execution_result=execution_result,
    )

    reports_dir = _reports_dir(notebook_path, cwd=cwd)
    reports_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = reports_dir / "notebook_qa.md"
    json_path = reports_dir / "notebook_qa.json"

    result = NotebookQaResult(
        status=status,
        notebook_file=str(notebook_path),
        total_cells=cell_summary["total_cells"],
        markdown_cells=cell_summary["markdown_cells"],
        code_cells=cell_summary["code_cells"],
        cells_with_outputs=cell_summary["cells_with_outputs"],
        cells_with_execution_count=cell_summary["cells_with_execution_count"],
        sections_found=sections_found,
        missing_sections=missing_sections,
        required_sections_passed=required_sections_passed,
        has_code_cells=has_code_cells,
        random_seed_found=random_seed_found,
        stale_output_detected=stale_output_detected,
        stale_output_warnings=stale_output_warnings,
        execute_requested=execute,
        execution_attempted=execution_result.attempted,
        execution_passed=execution_result.passed if execute else None,
        execution_runtime_seconds=execution_result.runtime_seconds,
        first_failing_cell_index=execution_result.first_failing_cell_index,
        execution_error_name=execution_result.error_name,
        execution_error_message=execution_result.error_message,
        execution_error=execution_result.error,
        report_markdown=str(markdown_path),
        report_json=str(json_path),
    )

    markdown_path.write_text(_markdown_report(result), encoding="utf-8")
    json_path.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")
    return result


def _sections_found(notebook: nbformat.NotebookNode) -> list[str]:
    found: list[str] = []
    for cell in notebook.cells:
        section = cell.metadata.get("repromath_section")
        if section in REQUIRED_SECTIONS and section not in found:
            found.append(section)
        if cell.cell_type == "markdown":
            for heading in _markdown_headings(cell.source):
                if heading in REQUIRED_SECTIONS and heading not in found:
                    found.append(heading)
            if "Title" not in found and _has_title_heading(cell.source):
                found.insert(0, "Title")
    return found


def _markdown_headings(source: str) -> list[str]:
    headings: list[str] = []
    for line in source.splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*$", line)
        if match is not None:
            headings.append(match.group(1).strip())
    return headings


def _has_title_heading(source: str) -> bool:
    return any(re.match(r"^#\s+\S+", line) for line in source.splitlines())


def _has_random_seed(code_source: str) -> bool:
    seed_patterns = (
        r"np\.random\.seed\s*\(",
        r"default_rng\s*\(",
        r"random\.seed\s*\(",
    )
    return any(re.search(pattern, code_source) for pattern in seed_patterns)


def _status(
    missing_sections: list[str],
    has_code_cells: bool,
    random_seed_found: bool,
    stale_output_detected: bool,
    execute_requested: bool,
    execution_result: NotebookExecutionResult,
) -> str:
    if missing_sections or not has_code_cells or not random_seed_found:
        return "FAIL"
    if execute_requested and not execution_result.passed:
        return "FAIL"
    if stale_output_detected:
        return "WARN"
    return "PASS"


def _reports_dir(notebook_path: Path, cwd: Path | None = None) -> Path:
    for parent in (notebook_path.parent, *notebook_path.parents):
        if (parent / "repromath.toml").is_file():
            return parent / "reports"
    return (cwd or Path.cwd()) / "reports"


def _markdown_report(result: NotebookQaResult) -> str:
    lines = [
        "# Notebook QA Report",
        "",
        f"Status: {result.status}",
        "",
        "## Input",
        "",
        f"* Notebook: {result.notebook_file}",
        f"* Execute requested: {'yes' if result.execute_requested else 'no'}",
        "",
        "## Structure",
        "",
        f"* Total cells: {result.total_cells}",
        f"* Markdown cells: {result.markdown_cells}",
        f"* Code cells: {result.code_cells}",
        f"* Cells with outputs: {result.cells_with_outputs}",
        f"* Cells with execution counts: {result.cells_with_execution_count}",
        f"* Required sections found: {len(result.sections_found)} / {len(REQUIRED_SECTIONS)}",
        f"* Required sections status: {'pass' if result.required_sections_passed else 'fail'}",
        f"* Code cells present: {'yes' if result.has_code_cells else 'no'}",
        f"* Random seed found: {'yes' if result.random_seed_found else 'no'}",
        f"* Stale output warning: {'yes' if result.stale_output_detected else 'no'}",
    ]
    if result.missing_sections:
        missing = ", ".join(f"`{section}`" for section in result.missing_sections)
        lines.append(f"* Missing sections: {missing}")
    else:
        lines.append("* Missing sections: none")

    if result.stale_output_warnings:
        lines.extend(["", "## Stale Output Warnings", ""])
        lines.extend(f"* {warning}" for warning in result.stale_output_warnings)

    lines.extend(["", "## Execution", ""])
    if not result.execute_requested:
        lines.append("* Execution was not requested.")
    elif result.execution_passed:
        runtime = _format_runtime(result.execution_runtime_seconds)
        lines.append(f"* Notebook executed successfully in {runtime}.")
    else:
        runtime = _format_runtime(result.execution_runtime_seconds)
        lines.append(f"* Notebook execution failed after {runtime}.")
        if result.first_failing_cell_index is not None:
            lines.append(
                f"* First failing cell index: {result.first_failing_cell_index}"
            )
        if result.execution_error_name:
            lines.append(f"* Error name: `{result.execution_error_name}`")
        if result.execution_error_message:
            lines.append(f"* Error message: `{result.execution_error_message}`")

    lines.extend(["", "## Suggested Next Actions", ""])
    actions = _suggested_actions(result)
    lines.extend(f"{index}. {action}" for index, action in enumerate(actions, start=1))
    lines.append("")
    return "\n".join(lines)


def _suggested_actions(result: NotebookQaResult) -> list[str]:
    actions: list[str] = []
    if result.missing_sections:
        actions.append("Add the missing study-first sections before treating the notebook as complete.")
    if not result.has_code_cells:
        actions.append("Add at least one code cell so the notebook can support a reproducible computation.")
    if not result.random_seed_found:
        actions.append("Set a random seed for toy experiments or stochastic diagnostics.")
    if result.stale_output_detected:
        actions.append("Clear or rerun stale-looking outputs before sharing the notebook.")
    if result.execute_requested and not result.execution_passed:
        actions.append("Fix the execution error and rerun notebook QA with `--execute`.")
    if not actions:
        actions.append("No immediate action needed for the checks that were run.")
    return actions


def _cell_summary(notebook: nbformat.NotebookNode) -> dict[str, int]:
    code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
    return {
        "total_cells": len(notebook.cells),
        "markdown_cells": sum(1 for cell in notebook.cells if cell.cell_type == "markdown"),
        "code_cells": len(code_cells),
        "cells_with_outputs": sum(1 for cell in code_cells if cell.get("outputs")),
        "cells_with_execution_count": sum(
            1 for cell in code_cells if cell.get("execution_count") is not None
        ),
    }


def _stale_output_warnings(notebook: nbformat.NotebookNode) -> list[str]:
    warnings: list[str] = []
    code_cells = [
        (index, cell)
        for index, cell in enumerate(notebook.cells)
        if cell.cell_type == "code"
    ]
    if not code_cells:
        return warnings

    execution_counts = [
        cell.get("execution_count")
        for _, cell in code_cells
        if cell.get("execution_count") is not None
    ]
    cells_with_outputs = [
        index
        for index, cell in code_cells
        if cell.get("outputs")
    ]
    for index, cell in code_cells:
        if cell.get("outputs") and cell.get("execution_count") is None:
            warnings.append(
                f"Code cell index {index} has outputs but no execution_count."
            )

    if execution_counts and len(execution_counts) < len(code_cells):
        warnings.append(
            f"Notebook appears partially executed: {len(execution_counts)} of "
            f"{len(code_cells)} code cells have execution counts."
        )

    if execution_counts != sorted(execution_counts):
        warnings.append("Execution counts are out of order.")

    if len(execution_counts) != len(set(execution_counts)):
        warnings.append("Execution counts contain duplicate values.")

    if cells_with_outputs and not execution_counts:
        warnings.append(
            "Notebook has saved outputs but no code cell execution counts."
        )

    return _unique(warnings)


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique_values: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        unique_values.append(value)
    return unique_values


def _format_runtime(seconds: float | None) -> str:
    if seconds is None:
        return "unknown runtime"
    return f"{seconds:.2f}s"
