"""Notebook QA checks for ReproMath."""

from __future__ import annotations

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
    sections_found: list[str]
    missing_sections: list[str]
    has_code_cells: bool
    random_seed_found: bool
    execute_requested: bool
    execution_attempted: bool
    execution_passed: bool | None
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
    sections_found = _sections_found(notebook)
    missing_sections = [
        section for section in REQUIRED_SECTIONS if section not in sections_found
    ]
    code_sources = [
        cell.source for cell in notebook.cells if cell.cell_type == "code"
    ]
    has_code_cells = bool(code_sources)
    random_seed_found = _has_random_seed("\n".join(code_sources))

    execution_result = (
        execute_notebook(notebook, notebook_path)
        if execute
        else NotebookExecutionResult(attempted=False, passed=False)
    )

    status = _status(
        missing_sections=missing_sections,
        has_code_cells=has_code_cells,
        random_seed_found=random_seed_found,
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
        sections_found=sections_found,
        missing_sections=missing_sections,
        has_code_cells=has_code_cells,
        random_seed_found=random_seed_found,
        execute_requested=execute,
        execution_attempted=execution_result.attempted,
        execution_passed=execution_result.passed if execute else None,
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
    execute_requested: bool,
    execution_result: NotebookExecutionResult,
) -> str:
    if missing_sections or not has_code_cells or not random_seed_found:
        return "FAIL"
    if execute_requested and not execution_result.passed:
        return "FAIL"
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
        f"* Required sections found: {len(result.sections_found)} / {len(REQUIRED_SECTIONS)}",
        f"* Code cells present: {'yes' if result.has_code_cells else 'no'}",
        f"* Random seed found: {'yes' if result.random_seed_found else 'no'}",
    ]
    if result.missing_sections:
        missing = ", ".join(f"`{section}`" for section in result.missing_sections)
        lines.append(f"* Missing sections: {missing}")
    else:
        lines.append("* Missing sections: none")

    lines.extend(["", "## Execution", ""])
    if not result.execute_requested:
        lines.append("* Execution was not requested.")
    elif result.execution_passed:
        lines.append("* Notebook executed successfully.")
    else:
        lines.append("* Notebook execution failed.")
        if result.execution_error:
            first_line = result.execution_error.splitlines()[0]
            lines.append(f"* Error: `{first_line}`")

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
    if result.execute_requested and not result.execution_passed:
        actions.append("Fix the execution error and rerun notebook QA with `--execute`.")
    if not actions:
        actions.append("No immediate action needed for the checks that were run.")
    return actions

