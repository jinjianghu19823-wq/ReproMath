"""Human- and machine-readable LaTeX QA reports."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json

from repromath import __version__
from repromath.latex.compile import LatexCompileResult, compile_with_latexmk
from repromath.latex.parse_log import (
    LatexLogSummary,
    LatexProblem,
    parse_latex_log_file,
)


@dataclass(frozen=True)
class LatexQaResult:
    status: str
    main_file: str
    engine: str
    engine_path: str | None
    compile_attempted: bool
    compile_returncode: int | None
    log_file: str | None
    pdf_file: str | None
    pdf_produced: bool
    page_count: int | None
    summary: LatexLogSummary
    report_markdown: str
    report_json: str


def run_latex_qa(tex_path: Path, cwd: Path | None = None) -> LatexQaResult:
    tex_path = tex_path.expanduser()
    if not tex_path.is_absolute():
        tex_path = (cwd or Path.cwd()) / tex_path
    tex_path = tex_path.resolve()

    if not tex_path.is_file():
        raise FileNotFoundError(f"LaTeX file not found: {tex_path}")

    compile_result = compile_with_latexmk(tex_path)
    log_path = tex_path.with_suffix(".log")
    summary = (
        parse_latex_log_file(log_path)
        if log_path.is_file()
        else LatexLogSummary()
    )

    pdf_path = tex_path.with_suffix(".pdf")
    pdf_produced = pdf_path.is_file() or summary.output_pdf is not None
    status = _status(compile_result, summary, log_path, pdf_produced)

    reports_dir = _reports_dir(tex_path, cwd=cwd)
    reports_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = reports_dir / "latex_qa.md"
    json_path = reports_dir / "latex_qa.json"

    result = LatexQaResult(
        status=status,
        main_file=str(tex_path),
        engine=compile_result.engine,
        engine_path=compile_result.engine_path,
        compile_attempted=compile_result.attempted,
        compile_returncode=compile_result.returncode,
        log_file=str(log_path) if log_path.is_file() else None,
        pdf_file=str(pdf_path) if pdf_path.is_file() else summary.output_pdf,
        pdf_produced=pdf_produced,
        page_count=summary.page_count,
        summary=summary,
        report_markdown=str(markdown_path),
        report_json=str(json_path),
    )

    markdown_path.write_text(_markdown_report(result, compile_result), encoding="utf-8")
    json_path.write_text(json.dumps(_json_report(result), indent=2), encoding="utf-8")

    return result


def _status(
    compile_result: LatexCompileResult,
    summary: LatexLogSummary,
    log_path: Path,
    pdf_produced: bool,
) -> str:
    if compile_result.attempted and compile_result.returncode not in {0, None}:
        return "FAIL"
    problem_status = _problem_status(summary)
    if problem_status is not None:
        return problem_status
    if not compile_result.attempted:
        return "WARN"
    if not log_path.is_file():
        return "WARN"
    if not pdf_produced:
        return "WARN"
    return "PASS"


def _problem_status(summary: LatexLogSummary) -> str | None:
    severities = {problem.severity for problem in summary.problems}
    if severities & {"fatal", "error"}:
        return "FAIL"
    if "warning" in severities:
        return "WARN"
    return None


def _reports_dir(tex_path: Path, cwd: Path | None = None) -> Path:
    for parent in (tex_path.parent, *tex_path.parents):
        if (parent / "repromath.toml").is_file():
            return parent / "reports"
    return (cwd or Path.cwd()) / "reports"


def _markdown_report(result: LatexQaResult, compile_result: LatexCompileResult) -> str:
    lines = [
        "# LaTeX QA Report",
        "",
        f"Status: {result.status}",
        "",
        "## Input",
        "",
        f"* Main file: {result.main_file}",
        f"* Engine: {result.engine}",
        f"* Engine path: {result.engine_path or 'not found'}",
        f"* Compile attempted: {'yes' if result.compile_attempted else 'no'}",
        f"* PDF produced: {'yes' if result.pdf_produced else 'no'}",
    ]
    if result.page_count is not None:
        lines.append(f"* Page count: {result.page_count}")
    if result.log_file is not None:
        lines.append(f"* Log file: {result.log_file}")

    lines.extend(["", "## Problems", ""])
    actionable_problems = [
        problem for problem in result.summary.problems if problem.severity != "info"
    ]
    if actionable_problems:
        lines.extend(_problem_sections(result.summary.problems))
    else:
        lines.append("* No problems found in the parsed LaTeX log.")
        info_lines = _problems_by_severity(result.summary.problems).get("info", [])
        if info_lines:
            lines.extend(["", "## Info", ""])
            lines.extend(_problem_lines(info_lines))

    if not result.compile_attempted:
        lines.extend(
            [
                "",
                "## Engine Warning",
                "",
                "* `latexmk` was not found on PATH, so ReproMath parsed an existing `.log` file if one was available.",
            ]
        )
    elif compile_result.returncode not in {0, None}:
        lines.extend(
            [
                "",
                "## Compiler Output",
                "",
                f"* `latexmk` exited with code {compile_result.returncode}.",
            ]
        )

    lines.extend(["", "## Suggested Next Actions", ""])
    lines.extend(_suggested_actions(result))
    lines.append("")
    return "\n".join(lines)


def _problem_sections(problems: list[LatexProblem]) -> list[str]:
    grouped = _problems_by_severity(problems)
    sections = [
        ("fatal", "## Fatal Errors"),
        ("error", "## Errors"),
        ("warning", "## Warnings"),
        ("info", "## Info"),
    ]
    lines: list[str] = []
    for severity, heading in sections:
        severity_problems = grouped.get(severity, [])
        if not severity_problems:
            continue
        lines.extend(["", heading, ""])
        lines.extend(_problem_lines(severity_problems))
    return lines


def _problems_by_severity(
    problems: list[LatexProblem],
) -> dict[str, list[LatexProblem]]:
    grouped: dict[str, list[LatexProblem]] = {}
    for problem in problems:
        grouped.setdefault(problem.severity, []).append(problem)
    return grouped


def _problem_lines(problems: list[LatexProblem]) -> list[str]:
    lines: list[str] = []
    for problem in problems:
        line_text = f" (line {problem.line})" if problem.line is not None else ""
        lines.append(f"* {problem.message}{line_text}")
        if problem.suggestion:
            lines.append(f"  Suggestion: {problem.suggestion}")
        if problem.context:
            lines.append(f"  Context: `{problem.context}`")
    return lines


def _suggested_actions(result: LatexQaResult) -> list[str]:
    summary = result.summary
    actions: list[str] = _unique_suggestions(summary.problems)
    if result.status == "WARN" and not result.compile_attempted:
        actions.append("Install `latexmk` or inspect the existing `.log` file manually.")
    if not result.pdf_produced:
        actions.append("Recompile after fixing errors and confirm that a PDF is produced.")
    if not actions:
        actions.append("No immediate action needed from the parsed log.")
    return [f"{index}. {action}" for index, action in enumerate(actions, start=1)]


def _unique_suggestions(problems: list[LatexProblem]) -> list[str]:
    suggestions: list[str] = []
    seen: set[str] = set()
    for problem in problems:
        if problem.severity == "info":
            continue
        suggestion = problem.suggestion
        if suggestion and suggestion not in seen:
            seen.add(suggestion)
            suggestions.append(suggestion)
    return suggestions


def _json_report(result: LatexQaResult) -> dict[str, object]:
    return {
        "schema_version": "repromath.latex_qa.v1",
        "tool_version": __version__,
        **asdict(result),
        "summary": asdict(result.summary),
        "problems": [asdict(problem) for problem in result.summary.problems],
    }
