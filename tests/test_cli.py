from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from repromath import __version__
from repromath.cli import run
from repromath.project_init import create_project


def test_run_version_prints_package_version(capsys) -> None:
    exit_code = run(["--version"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out.strip() == f"repromath {__version__}"


def test_module_version_command_works() -> None:
    project_root = Path(__file__).resolve().parents[1]
    env = {
        **os.environ,
        "PYTHONPATH": str(project_root / "src"),
    }

    completed = subprocess.run(
        [sys.executable, "-m", "repromath.cli", "--version"],
        check=True,
        capture_output=True,
        env=env,
        text=True,
    )

    assert completed.stdout.strip() == f"repromath {__version__}"


def test_init_dissertation_creates_expected_structure(tmp_path: Path) -> None:
    project_path = tmp_path / "my-dissertation"

    exit_code = run(["init", "dissertation", str(project_path)])

    assert exit_code == 0
    assert (project_path / "repromath.toml").is_file()
    assert (project_path / "README.md").is_file()
    assert (project_path / "notebooks").is_dir()
    assert (project_path / "figures").is_dir()
    assert (project_path / "reports").is_dir()
    assert (project_path / "sources").is_dir()
    assert (project_path / "thesis" / "main.tex").is_file()
    assert (project_path / "thesis" / "sections").is_dir()
    assert (project_path / "thesis" / "figures").is_dir()

    config = (project_path / "repromath.toml").read_text(encoding="utf-8")
    assert 'name = "my-dissertation"' in config
    assert 'type = "dissertation"' in config
    assert 'main_tex = "thesis/main.tex"' in config


def test_init_paper_study_creates_expected_structure(tmp_path: Path) -> None:
    project_path = create_project(
        "paper-study",
        "my-paper-study",
        base_dir=tmp_path,
    )

    assert (project_path / "repromath.toml").is_file()
    assert (project_path / "notebooks").is_dir()
    assert (project_path / "notes").is_dir()
    assert (project_path / "sources").is_dir()

    config = (project_path / "repromath.toml").read_text(encoding="utf-8")
    assert 'type = "paper-study"' in config
    assert "main_tex" not in config


def test_init_numerical_experiment_creates_expected_structure(tmp_path: Path) -> None:
    project_path = create_project(
        "numerical-experiment",
        "my-experiment",
        base_dir=tmp_path,
    )

    assert (project_path / "repromath.toml").is_file()
    assert (project_path / "experiments").is_dir()
    assert (project_path / "notebooks").is_dir()
    assert (project_path / "figures").is_dir()
    assert (project_path / "reports").is_dir()

    config = (project_path / "repromath.toml").read_text(encoding="utf-8")
    assert 'type = "numerical-experiment"' in config


def test_init_refuses_to_overwrite_existing_project(tmp_path: Path, capsys) -> None:
    project_path = tmp_path / "existing-project"
    project_path.mkdir()
    sentinel = project_path / "keep.txt"
    sentinel.write_text("do not overwrite", encoding="utf-8")

    exit_code = run(["init", "dissertation", str(project_path)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "already exists" in captured.err
    assert sentinel.read_text(encoding="utf-8") == "do not overwrite"
