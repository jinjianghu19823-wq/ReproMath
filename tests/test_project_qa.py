from __future__ import annotations

import json
from pathlib import Path

from repromath import __version__
from repromath.cli import run
from repromath.notebook.scaffold import create_notebook_scaffold
from repromath.project_init import create_project
from repromath.project_qa import run_project_qa


def test_project_qa_works_on_generated_dissertation(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr("repromath.latex.compile.shutil.which", lambda _: None)
    project_root = create_project("dissertation", "demo-dissertation", base_dir=tmp_path)

    result = run_project_qa(project_root)

    assert result.status == "WARN"
    assert result.missing_files == []
    assert result.latex_status == "WARN"
    assert result.source_coverage_summary.artifact_count == 0
    assert (project_root / "reports" / "project_qa.md").is_file()
    assert (project_root / "reports" / "project_qa.json").is_file()
    assert (project_root / "reports" / "latex_qa.md").is_file()


def test_project_qa_reports_missing_declared_artifact_files(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    (project_root / "repromath.toml").write_text(
        """
[project]
name = "demo"
type = "paper-study"

[paths]
reports = "reports"

[[artifacts]]
id = "fig_missing"
type = "figure"
output = "figures/missing.pdf"
used_in = "notes/missing.md"
""",
        encoding="utf-8",
    )

    result = run_project_qa(project_root)

    assert result.status == "FAIL"
    assert "figures/missing.pdf" in result.missing_files
    assert "notes/missing.md" in result.missing_files
    assert result.artifact_checks[0].source is None
    assert result.artifact_checks[0].status == "FAIL"
    assert result.source_coverage_summary.missing_outputs == 1
    assert result.source_coverage_summary.missing_used_in_files == 1

    markdown_report = (project_root / "reports" / "project_qa.md").read_text(
        encoding="utf-8"
    )
    assert "| id | type | output | output_exists | source | used_in | used_in_exists | status |" in markdown_report
    assert "| fig_missing | figure | figures/missing.pdf | no | -" in markdown_report
    assert "notes/missing.md | no | FAIL |" in markdown_report

    json_report = json.loads(
        (project_root / "reports" / "project_qa.json").read_text(encoding="utf-8")
    )
    assert json_report["schema_version"] == "repromath.project_qa.v1"
    assert json_report["tool_version"] == __version__
    assert json_report["artifact_checks"][0]["status"] == "FAIL"
    assert json_report["source_coverage_summary"]["missing_outputs"] == 1


def test_project_qa_runs_notebook_qa_for_declared_notebook(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    notebook_path = create_notebook_scaffold("SVD", base_dir=project_root)
    (project_root / "repromath.toml").write_text(
        f"""
[project]
name = "demo"
type = "numerical-experiment"

[paths]
reports = "reports"

[[artifacts]]
id = "notebook_svd"
type = "notebook"
output = "{notebook_path.relative_to(project_root)}"
source = "toy"
role = "diagnostics"
""",
        encoding="utf-8",
    )

    result = run_project_qa(project_root)

    assert result.status == "PASS"
    assert result.artifact_checks[0].source == "toy"
    assert result.artifact_checks[0].status == "PASS"
    assert result.source_coverage_summary.artifact_count == 1
    assert result.source_coverage_summary.artifacts_with_source == 1
    assert result.notebook_statuses == [
        {
            "notebook": str(notebook_path),
            "status": "PASS",
            "report": str(project_root / "reports" / "notebook_qa.md"),
        }
    ]


def test_cli_project_qa_writes_reports(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("repromath.latex.compile.shutil.which", lambda _: None)
    project_root = create_project("dissertation", "demo", base_dir=tmp_path)
    monkeypatch.chdir(project_root)

    exit_code = run(["qa", "project"])

    assert exit_code == 0
    assert (project_root / "reports" / "project_qa.md").is_file()
    assert (project_root / "reports" / "project_qa.json").is_file()
