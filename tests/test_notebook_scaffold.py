from __future__ import annotations

from pathlib import Path

import nbformat

from repromath.cli import run
from repromath.notebook.scaffold import create_notebook_scaffold, slugify
from repromath.notebook.sections import REQUIRED_SECTIONS


def test_slugify_topic_for_default_notebook_name() -> None:
    assert slugify("truncated HOSVD") == "truncated-hosvd"
    assert slugify("  SVD rank-1 demo ") == "svd-rank-1-demo"


def test_create_notebook_scaffold_has_required_sections(tmp_path: Path) -> None:
    notebook_path = create_notebook_scaffold("truncated HOSVD", base_dir=tmp_path)

    assert notebook_path == tmp_path / "notebooks" / "truncated-hosvd.ipynb"
    notebook = nbformat.read(notebook_path, as_version=4)
    section_names = [
        cell.metadata.get("repromath_section")
        for cell in notebook.cells
        if cell.metadata.get("repromath_section")
    ]

    assert section_names == list(REQUIRED_SECTIONS)
    assert notebook.metadata["repromath"]["topic"] == "truncated HOSVD"


def test_notebook_scaffold_contains_starter_code(tmp_path: Path) -> None:
    notebook_path = create_notebook_scaffold("SVD", base_dir=tmp_path)
    notebook = nbformat.read(notebook_path, as_version=4)
    code_source = "\n".join(
        cell.source for cell in notebook.cells if cell.cell_type == "code"
    )

    assert "import numpy as np" in code_source
    assert "import matplotlib.pyplot as plt" in code_source
    assert "np.random.default_rng(0)" in code_source
    assert "Placeholder for toy data" in code_source
    assert "Placeholder for the recommended algorithm" in code_source
    assert "Placeholder for diagnostics" in code_source


def test_hosvd_topic_gets_light_specialized_text(tmp_path: Path) -> None:
    notebook_path = create_notebook_scaffold("truncated HOSVD", base_dir=tmp_path)
    notebook = nbformat.read(notebook_path, as_version=4)
    markdown_source = "\n".join(
        cell.source for cell in notebook.cells if cell.cell_type == "markdown"
    )

    assert "mode unfoldings" in markdown_source
    assert "Tucker core" in markdown_source


def test_cli_scaffold_notebook_writes_default_path(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    exit_code = run(["scaffold", "notebook", "--topic", "truncated HOSVD"])

    assert exit_code == 0
    assert (tmp_path / "notebooks" / "truncated-hosvd.ipynb").is_file()


def test_scaffold_notebook_refuses_to_overwrite(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    assert run(["scaffold", "notebook", "--topic", "SVD"]) == 0

    exit_code = run(["scaffold", "notebook", "--topic", "SVD"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Refusing to overwrite existing notebook" in captured.err
