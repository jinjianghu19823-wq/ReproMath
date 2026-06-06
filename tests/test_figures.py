from __future__ import annotations

from pathlib import Path

from repromath.cli import run
from repromath.figures.registry import FIGURE_RECIPES
from repromath.figures.scaffold import create_figure_recipe


EXPECTED_RECIPES = {
    "svd-rank-one",
    "tensor-fibers",
    "tensor-slices",
    "tensor-unfolding",
    "singular-value-decay",
    "storage-vs-rank",
}


def test_expected_figure_recipes_are_registered() -> None:
    assert set(FIGURE_RECIPES) == EXPECTED_RECIPES


def test_each_figure_recipe_creates_script_note_and_pdf(tmp_path: Path) -> None:
    for recipe_name in sorted(EXPECTED_RECIPES):
        result = create_figure_recipe(recipe_name, base_dir=tmp_path / recipe_name)

        assert Path(result.script_path).is_file()
        assert Path(result.note_path).is_file()
        assert Path(result.figure_path).is_file()
        assert Path(result.figure_path).stat().st_size > 0


def test_cli_scaffold_figure_creates_default_files(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    exit_code = run(["scaffold", "figure", "tensor-unfolding"])

    assert exit_code == 0
    assert (tmp_path / "figures" / "tensor-unfolding.py").is_file()
    assert (tmp_path / "figures" / "tensor-unfolding.md").is_file()
    assert (tmp_path / "figures" / "tensor-unfolding.pdf").is_file()


def test_scaffold_figure_refuses_to_overwrite(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    assert run(["scaffold", "figure", "singular-value-decay"]) == 0

    exit_code = run(["scaffold", "figure", "singular-value-decay"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Refusing to overwrite existing figure files" in captured.err
