"""Project-level QA for ReproMath projects."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json

from repromath.config import ConfigError, ProjectConfig, load_project_config
from repromath.latex.report import LatexQaResult, run_latex_qa
from repromath.notebook.qa import NotebookQaResult, run_notebook_qa
from repromath.provenance.schema import Artifact


@dataclass(frozen=True)
class ArtifactCheck:
    id: str
    artifact_type: str
    output: str
    output_exists: bool
    used_in: str | None = None
    used_in_exists: bool | None = None


@dataclass(frozen=True)
class ProjectQaResult:
    status: str
    project_root: str
    config_file: str
    missing_files: list[str]
    artifact_checks: list[ArtifactCheck]
    latex_status: str | None
    latex_report: str | None
    notebook_statuses: list[dict[str, str]]
    report_markdown: str
    report_json: str


def run_project_qa(project_root: Path | None = None) -> ProjectQaResult:
    config = load_project_config(project_root)
    reports_dir = config.root / config.paths.get("reports", "reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    missing_files: list[str] = []
    artifact_checks = _check_artifacts(config, missing_files)
    latex_result = _run_latex_if_available(config, missing_files)
    notebook_results = _run_notebook_checks(config)

    status = _project_status(missing_files, latex_result, notebook_results)
    markdown_path = reports_dir / "project_qa.md"
    json_path = reports_dir / "project_qa.json"

    result = ProjectQaResult(
        status=status,
        project_root=str(config.root),
        config_file=str(config.config_path),
        missing_files=missing_files,
        artifact_checks=artifact_checks,
        latex_status=latex_result.status if latex_result is not None else None,
        latex_report=latex_result.report_markdown if latex_result is not None else None,
        notebook_statuses=[
            {
                "notebook": notebook.notebook_file,
                "status": notebook.status,
                "report": notebook.report_markdown,
            }
            for notebook in notebook_results
        ],
        report_markdown=str(markdown_path),
        report_json=str(json_path),
    )
    markdown_path.write_text(_markdown_report(result, config), encoding="utf-8")
    json_path.write_text(json.dumps(_json_report(result), indent=2), encoding="utf-8")
    return result


def _check_artifacts(config: ProjectConfig, missing_files: list[str]) -> list[ArtifactCheck]:
    checks: list[ArtifactCheck] = []
    for artifact in config.artifacts:
        output_path = config.root / artifact.output
        output_exists = output_path.is_file()
        used_in_exists = None
        if artifact.used_in:
            used_in_exists = (config.root / artifact.used_in).is_file()
        check = ArtifactCheck(
            id=artifact.id,
            artifact_type=artifact.artifact_type,
            output=artifact.output,
            output_exists=output_exists,
            used_in=artifact.used_in,
            used_in_exists=used_in_exists,
        )
        checks.append(check)
        if not output_exists:
            missing_files.append(artifact.output)
        if artifact.used_in and not used_in_exists:
            missing_files.append(artifact.used_in)
    return checks


def _run_latex_if_available(
    config: ProjectConfig,
    missing_files: list[str],
) -> LatexQaResult | None:
    if config.main_tex is None:
        return None
    tex_path = config.root / config.main_tex
    if not tex_path.is_file():
        missing_files.append(config.main_tex)
        return None
    return run_latex_qa(tex_path, cwd=config.root)


def _run_notebook_checks(config: ProjectConfig) -> list[NotebookQaResult]:
    results: list[NotebookQaResult] = []
    for artifact in config.artifacts:
        if artifact.artifact_type != "notebook":
            continue
        notebook_path = config.root / artifact.output
        if notebook_path.is_file():
            results.append(run_notebook_qa(notebook_path, cwd=config.root))
    return results


def _project_status(
    missing_files: list[str],
    latex_result: LatexQaResult | None,
    notebook_results: list[NotebookQaResult],
) -> str:
    if missing_files:
        return "FAIL"
    child_statuses = []
    if latex_result is not None:
        child_statuses.append(latex_result.status)
    child_statuses.extend(notebook.status for notebook in notebook_results)
    if any(status == "FAIL" for status in child_statuses):
        return "FAIL"
    if any(status == "WARN" for status in child_statuses):
        return "WARN"
    return "PASS"


def _markdown_report(result: ProjectQaResult, config: ProjectConfig) -> str:
    lines = [
        "# Project QA Report",
        "",
        f"Status: {result.status}",
        "",
        "## Project",
        "",
        f"* Name: {config.name}",
        f"* Type: {config.project_type or 'unknown'}",
        f"* Root: {result.project_root}",
        f"* Config: {result.config_file}",
        "",
        "## Declared Files",
        "",
    ]
    if result.artifact_checks:
        for check in result.artifact_checks:
            output_state = "present" if check.output_exists else "missing"
            lines.append(f"* `{check.output}` ({check.artifact_type}): {output_state}")
            if check.used_in is not None:
                used_in_state = "present" if check.used_in_exists else "missing"
                lines.append(f"* `{check.used_in}` (used_in): {used_in_state}")
    else:
        lines.append("* No artifact entries declared yet.")

    lines.extend(["", "## Child QA", ""])
    if result.latex_status is not None:
        lines.append(f"* LaTeX QA: {result.latex_status} ({result.latex_report})")
    else:
        lines.append("* LaTeX QA: not run")
    if result.notebook_statuses:
        for item in result.notebook_statuses:
            lines.append(f"* Notebook QA: {item['status']} ({item['notebook']})")
    else:
        lines.append("* Notebook QA: no declared notebook artifacts found")

    lines.extend(["", "## Missing Files", ""])
    if result.missing_files:
        for missing in result.missing_files:
            lines.append(f"* `{missing}`")
    else:
        lines.append("* None")

    lines.extend(["", "## Suggested Next Actions", ""])
    actions = _suggested_actions(result)
    lines.extend(f"{index}. {action}" for index, action in enumerate(actions, start=1))
    lines.append("")
    return "\n".join(lines)


def _suggested_actions(result: ProjectQaResult) -> list[str]:
    actions: list[str] = []
    if result.missing_files:
        actions.append("Create or correct the missing declared files in `repromath.toml`.")
    if result.latex_status == "FAIL":
        actions.append("Open `reports/latex_qa.md` and fix the LaTeX problems first.")
    if any(item["status"] == "FAIL" for item in result.notebook_statuses):
        actions.append("Open `reports/notebook_qa.md` and fix notebook structure problems.")
    if result.status == "WARN":
        actions.append("Review warning-level child QA reports before considering the project clean.")
    if not actions:
        actions.append("No immediate action needed for the checks that were run.")
    return actions


def _json_report(result: ProjectQaResult) -> dict[str, object]:
    return asdict(result)


def project_qa_from_cli() -> ProjectQaResult:
    try:
        return run_project_qa()
    except ConfigError:
        raise

