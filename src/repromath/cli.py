"""Command-line interface for ReproMath."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from repromath import __version__
from repromath.config import ConfigError
from repromath.figures.registry import FIGURE_RECIPES
from repromath.figures.scaffold import FigureScaffoldError, create_figure_recipe
from repromath.latex.report import run_latex_qa
from repromath.notebook.scaffold import (
    NotebookScaffoldError,
    create_notebook_scaffold,
)
from repromath.notebook.qa import run_notebook_qa
from repromath.project_init import PROJECT_TEMPLATES, ProjectInitError, create_project
from repromath.project_qa import run_project_qa


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="repromath",
        description=(
            "A lightweight CLI toolkit for reproducible mathematical research "
            "projects."
        ),
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show the installed ReproMath version and exit.",
    )
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser(
        "init",
        help="Initialize a new ReproMath project.",
    )
    init_parser.add_argument(
        "project_type",
        choices=sorted(PROJECT_TEMPLATES),
        help="Type of research project to create.",
    )
    init_parser.add_argument(
        "project_name",
        help="Project directory to create.",
    )

    qa_parser = subparsers.add_parser(
        "qa",
        help="Run QA checks for research artifacts.",
    )
    qa_subparsers = qa_parser.add_subparsers(dest="qa_command")
    latex_parser = qa_subparsers.add_parser(
        "latex",
        help="Compile or parse a LaTeX file and write QA reports.",
    )
    latex_parser.add_argument(
        "tex_path",
        help="Path to the main .tex file.",
    )
    notebook_qa_parser = qa_subparsers.add_parser(
        "notebook",
        help="Check notebook structure and optionally execute it.",
    )
    notebook_qa_parser.add_argument(
        "notebook_path",
        help="Path to the .ipynb file.",
    )
    notebook_qa_parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute the notebook during QA.",
    )
    qa_subparsers.add_parser(
        "project",
        help="Run available QA checks declared by repromath.toml.",
    )

    scaffold_parser = subparsers.add_parser(
        "scaffold",
        help="Create notebooks, figures, or other research artifacts.",
    )
    scaffold_subparsers = scaffold_parser.add_subparsers(dest="scaffold_command")
    notebook_parser = scaffold_subparsers.add_parser(
        "notebook",
        help="Create a study-first Jupyter notebook.",
    )
    notebook_parser.add_argument(
        "--topic",
        required=True,
        help="Mathematical topic for the notebook.",
    )
    figure_parser = scaffold_subparsers.add_parser(
        "figure",
        help="Create and run a dissertation-friendly figure recipe.",
    )
    figure_parser.add_argument(
        "recipe_name",
        choices=sorted(FIGURE_RECIPES),
        help="Built-in figure recipe name.",
    )
    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print(f"repromath {__version__}")
        return 0

    if args.command == "init":
        try:
            project_path = create_project(args.project_type, args.project_name)
        except ProjectInitError as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1

        print(f"Created {args.project_type} project at {project_path}")
        return 0

    if args.command == "qa" and args.qa_command == "latex":
        try:
            result = run_latex_qa(Path(args.tex_path))
        except FileNotFoundError as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1

        print(f"LaTeX QA status: {result.status}")
        print(f"Markdown report: {result.report_markdown}")
        print(f"JSON report: {result.report_json}")
        return 0 if result.status in {"PASS", "WARN"} else 1

    if args.command == "qa" and args.qa_command == "notebook":
        try:
            result = run_notebook_qa(Path(args.notebook_path), execute=args.execute)
        except FileNotFoundError as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1

        print(f"Notebook QA status: {result.status}")
        print(f"Markdown report: {result.report_markdown}")
        print(f"JSON report: {result.report_json}")
        return 0 if result.status == "PASS" else 1

    if args.command == "qa" and args.qa_command == "project":
        try:
            result = run_project_qa()
        except ConfigError as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1

        print(f"Project QA status: {result.status}")
        print(f"Markdown report: {result.report_markdown}")
        print(f"JSON report: {result.report_json}")
        return 0 if result.status in {"PASS", "WARN"} else 1

    if args.command == "scaffold" and args.scaffold_command == "notebook":
        try:
            notebook_path = create_notebook_scaffold(args.topic)
        except NotebookScaffoldError as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1

        print(f"Created notebook scaffold at {notebook_path}")
        return 0

    if args.command == "scaffold" and args.scaffold_command == "figure":
        try:
            result = create_figure_recipe(args.recipe_name)
        except FigureScaffoldError as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1

        print(f"Created figure recipe script: {result.script_path}")
        print(f"Created figure output: {result.figure_path}")
        print(f"Created figure note: {result.note_path}")
        return 0

    parser.print_help()
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
