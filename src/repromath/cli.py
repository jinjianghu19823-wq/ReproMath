"""Command-line interface for ReproMath."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import textwrap

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
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_dedent(
            """
            Typical workflow:
              paper/theorem notes -> notebook -> figure -> LaTeX section -> QA reports

            Examples:
              repromath init dissertation my-project
              repromath scaffold notebook --topic "truncated HOSVD"
              repromath qa project
            """
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
        description=(
            "Create a small research project scaffold with repromath.toml, "
            "notebooks, figures, reports, and sources directories."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_dedent(
            """
            Examples:
              repromath init dissertation my-dissertation
              repromath init paper-study kolda-bader-study
              repromath init numerical-experiment svd-stability-demo

            Safety:
              ReproMath refuses to overwrite an existing project directory.
            """
        ),
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
        description=(
            "Run lightweight QA checks and write human-readable Markdown plus "
            "machine-readable JSON reports."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_dedent(
            """
            Examples:
              repromath qa latex thesis/main.tex
              repromath qa notebook notebooks/truncated-hosvd.ipynb
              repromath qa notebook notebooks/truncated-hosvd.ipynb --execute
              repromath qa project

            Reports:
              LaTeX, notebook, and project QA reports are written to reports/.
            """
        ),
    )
    qa_subparsers = qa_parser.add_subparsers(dest="qa_command")
    latex_parser = qa_subparsers.add_parser(
        "latex",
        help="Compile or parse a LaTeX file and write QA reports.",
        description=(
            "Attempt to compile a LaTeX main file with latexmk, then parse the "
            ".log file for common writing and build problems."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_dedent(
            """
            Example:
              repromath qa latex thesis/main.tex

            Output:
              reports/latex_qa.md
              reports/latex_qa.json
            """
        ),
    )
    latex_parser.add_argument(
        "tex_path",
        help="Path to the main .tex file.",
    )
    notebook_qa_parser = qa_subparsers.add_parser(
        "notebook",
        help="Check notebook structure and optionally execute it.",
        description=(
            "Check that a mathematical research notebook has the expected "
            "study-first sections, code cells, and a random seed. Execution is "
            "optional."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_dedent(
            """
            Examples:
              repromath qa notebook notebooks/truncated-hosvd.ipynb
              repromath qa notebook notebooks/truncated-hosvd.ipynb --execute

            Output:
              reports/notebook_qa.md
              reports/notebook_qa.json
            """
        ),
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
        description=(
            "Read repromath.toml, check declared artifacts, and run available "
            "LaTeX and notebook QA checks."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_dedent(
            """
            Example:
              repromath qa project

            Output:
              reports/project_qa.md
              reports/project_qa.json
            """
        ),
    )

    scaffold_parser = subparsers.add_parser(
        "scaffold",
        help="Create notebooks, figures, or other research artifacts.",
        description=(
            "Create deterministic starter artifacts for mathematical research "
            "projects."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_dedent(
            """
            Examples:
              repromath scaffold notebook --topic "truncated HOSVD"
              repromath scaffold figure tensor-unfolding
              repromath scaffold figure singular-value-decay
            """
        ),
    )
    scaffold_subparsers = scaffold_parser.add_subparsers(dest="scaffold_command")
    notebook_parser = scaffold_subparsers.add_parser(
        "notebook",
        help="Create a study-first Jupyter notebook.",
        description=(
            "Create a Jupyter notebook with study-first mathematical sections "
            "and starter NumPy/Matplotlib cells."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_dedent(
            """
            Example:
              repromath scaffold notebook --topic "truncated HOSVD"

            Default output:
              notebooks/<slugified-topic>.ipynb
            """
        ),
    )
    notebook_parser.add_argument(
        "--topic",
        required=True,
        help="Mathematical topic for the notebook.",
    )
    figure_parser = scaffold_subparsers.add_parser(
        "figure",
        help="Create and run a dissertation-friendly figure recipe.",
        description=(
            "Create a deterministic Matplotlib figure script, run it, and save "
            "a PDF plus a short Markdown note."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_dedent(
            """
            Examples:
              repromath scaffold figure tensor-unfolding
              repromath scaffold figure storage-vs-rank

            Supported recipes:
              svd-rank-one, tensor-fibers, tensor-slices, tensor-unfolding,
              singular-value-decay, storage-vs-rank
            """
        ),
    )
    figure_parser.add_argument(
        "recipe_name",
        choices=sorted(FIGURE_RECIPES),
        help="Built-in figure recipe name.",
    )
    return parser


def _dedent(text: str) -> str:
    return textwrap.dedent(text).strip()


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
        print(
            "Cells: "
            f"{result.total_cells} total, "
            f"{result.markdown_cells} markdown, "
            f"{result.code_cells} code"
        )
        if result.stale_output_detected:
            print("Stale outputs: warnings found")
        if result.execute_requested:
            if result.execution_passed:
                runtime = _format_seconds(result.execution_runtime_seconds)
                print(f"Execution: PASS in {runtime}")
            else:
                runtime = _format_seconds(result.execution_runtime_seconds)
                print(f"Execution: FAIL after {runtime}")
                if result.first_failing_cell_index is not None:
                    print(
                        "First failing cell index: "
                        f"{result.first_failing_cell_index}"
                    )
                if result.execution_error_name:
                    print(f"Execution error: {result.execution_error_name}")
        print(f"Markdown report: {result.report_markdown}")
        print(f"JSON report: {result.report_json}")
        return 0 if result.status in {"PASS", "WARN"} else 1

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


def _format_seconds(seconds: float | None) -> str:
    if seconds is None:
        return "unknown runtime"
    return f"{seconds:.2f}s"


if __name__ == "__main__":
    main()
