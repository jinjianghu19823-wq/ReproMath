from __future__ import annotations

import json
from pathlib import Path

from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook
import nbformat

from repromath.cli import run
from repromath.notebook.qa import run_notebook_qa
from repromath.notebook.scaffold import create_notebook_scaffold


def test_generated_notebook_passes_structural_qa(tmp_path: Path) -> None:
    notebook_path = create_notebook_scaffold("truncated HOSVD", base_dir=tmp_path)

    result = run_notebook_qa(notebook_path, cwd=tmp_path)

    assert result.status == "PASS"
    assert result.missing_sections == []
    assert result.has_code_cells
    assert result.random_seed_found
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
    assert result.has_code_cells
    assert result.random_seed_found


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
