from __future__ import annotations

from pathlib import Path

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
