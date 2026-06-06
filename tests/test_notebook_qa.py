from __future__ import annotations

import json
from pathlib import Path

import pytest
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook, new_output
import nbformat

from repromath.cli import run
from repromath.notebook.execute import NotebookExecutionResult
from repromath.notebook.qa import run_notebook_qa
from repromath.notebook.scaffold import create_notebook_scaffold


def test_generated_notebook_passes_structural_qa(tmp_path: Path) -> None:
    notebook_path = create_notebook_scaffold("truncated HOSVD", base_dir=tmp_path)

    result = run_notebook_qa(notebook_path, cwd=tmp_path)

    assert result.status == "PASS"
    assert result.missing_sections == []
    assert result.has_code_cells
    assert result.random_seed_found
    assert result.required_sections_passed
    assert result.total_cells > result.code_cells
    assert result.markdown_cells > 0
    assert result.code_cells > 0
    assert result.cells_with_outputs == 0
    assert result.cells_with_execution_count == 0
    assert not result.stale_output_detected
    assert (tmp_path / "reports" / "notebook_qa.md").is_file()
    assert (tmp_path / "reports" / "notebook_qa.json").is_file()


def test_notebook_qa_fails_when_sections_are_missing(tmp_path: Path) -> None:
    notebook_path = tmp_path / "notebooks" / "broken.ipynb"
    notebook_path.parent.mkdir()
    notebook = new_notebook(
        cells=[
            new_markdown_cell("# Broken Notebook\n"),
            new_code_cell("import numpy as np\nrng = np.random.default_rng(0)\n"),
        ]
    )
    nbformat.write(notebook, notebook_path)

    result = run_notebook_qa(notebook_path, cwd=tmp_path)

    assert result.status == "FAIL"
    assert "Motivation" in result.missing_sections
    assert not result.required_sections_passed
    assert result.has_code_cells
    assert result.random_seed_found


def test_notebook_qa_warns_for_stale_outputs(tmp_path: Path) -> None:
    notebook_path = create_notebook_scaffold("SVD", base_dir=tmp_path)
    notebook = nbformat.read(notebook_path, as_version=4)
    first_code_cell = next(cell for cell in notebook.cells if cell.cell_type == "code")
    first_code_cell.outputs = [
        new_output(output_type="stream", name="stdout", text="old output\n")
    ]
    first_code_cell.execution_count = None
    nbformat.write(notebook, notebook_path)

    result = run_notebook_qa(notebook_path, cwd=tmp_path)

    assert result.status == "WARN"
    assert result.stale_output_detected
    assert result.cells_with_outputs == 1
    assert result.cells_with_execution_count == 0
    assert "outputs but no execution_count" in result.stale_output_warnings[0]
    markdown_report = (tmp_path / "reports" / "notebook_qa.md").read_text(
        encoding="utf-8"
    )
    assert "## Stale Output Warnings" in markdown_report


def test_notebook_qa_execute_captures_failure(tmp_path: Path) -> None:
    notebook_path = create_notebook_scaffold("SVD", base_dir=tmp_path)
    notebook = nbformat.read(notebook_path, as_version=4)
    notebook.cells.append(new_code_cell("raise RuntimeError('boom')\n"))
    nbformat.write(notebook, notebook_path)

    result = run_notebook_qa(notebook_path, execute=True, cwd=tmp_path)

    assert result.status == "FAIL"
    assert result.execution_attempted
    assert result.execution_passed is False
    assert result.execution_error is not None
    assert result.execution_error


def test_notebook_qa_records_execution_failure_summary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    notebook_path = create_notebook_scaffold("SVD", base_dir=tmp_path)

    def fake_execute_notebook(
        notebook: nbformat.NotebookNode,
        notebook_path: Path,
    ) -> NotebookExecutionResult:
        return NotebookExecutionResult(
            attempted=True,
            passed=False,
            error="RuntimeError: boom",
            runtime_seconds=0.25,
            first_failing_cell_index=7,
            error_name="RuntimeError",
            error_message="boom",
        )

    monkeypatch.setattr(
        "repromath.notebook.qa.execute_notebook",
        fake_execute_notebook,
    )

    result = run_notebook_qa(notebook_path, execute=True, cwd=tmp_path)

    assert result.status == "FAIL"
    assert result.execution_attempted
    assert result.execution_passed is False
    assert result.execution_runtime_seconds == 0.25
    assert result.first_failing_cell_index == 7
    assert result.execution_error_name == "RuntimeError"
    assert result.execution_error_message == "boom"

    json_report = json.loads(
        (tmp_path / "reports" / "notebook_qa.json").read_text(encoding="utf-8")
    )
    assert json_report["first_failing_cell_index"] == 7
    assert json_report["execution_error_name"] == "RuntimeError"
    markdown_report = (tmp_path / "reports" / "notebook_qa.md").read_text(
        encoding="utf-8"
    )
    assert "First failing cell index: 7" in markdown_report
    assert "Error name: `RuntimeError`" in markdown_report


def test_cli_notebook_qa_writes_reports_in_project_root(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    (project_root / "repromath.toml").write_text("[project]\nname = \"x\"\n", encoding="utf-8")
    notebook_path = create_notebook_scaffold("SVD", base_dir=project_root)

    exit_code = run(["qa", "notebook", str(notebook_path)])

    assert exit_code == 0
    markdown_report = project_root / "reports" / "notebook_qa.md"
    json_report = project_root / "reports" / "notebook_qa.json"
    assert markdown_report.is_file()
    assert json_report.is_file()
    data = json.loads(json_report.read_text(encoding="utf-8"))
    assert data["status"] == "PASS"
    assert data["total_cells"] > data["code_cells"]
    assert data["stale_output_detected"] is False


def test_cli_notebook_qa_execute_prints_summary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    (project_root / "repromath.toml").write_text(
        "[project]\nname = \"x\"\n",
        encoding="utf-8",
    )
    notebook_path = create_notebook_scaffold("SVD", base_dir=project_root)

    def fake_execute_notebook(
        notebook: nbformat.NotebookNode,
        notebook_path: Path,
    ) -> NotebookExecutionResult:
        return NotebookExecutionResult(
            attempted=True,
            passed=False,
            error="RuntimeError: boom",
            runtime_seconds=0.25,
            first_failing_cell_index=7,
            error_name="RuntimeError",
            error_message="boom",
        )

    monkeypatch.setattr(
        "repromath.notebook.qa.execute_notebook",
        fake_execute_notebook,
    )

    exit_code = run(["qa", "notebook", str(notebook_path), "--execute"])

    assert exit_code == 1
    output = capsys.readouterr().out
    assert "Cells:" in output
    assert "Execution: FAIL after 0.25s" in output
    assert "First failing cell index: 7" in output
    assert "Execution error: RuntimeError" in output
