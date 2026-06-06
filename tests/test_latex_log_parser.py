from __future__ import annotations

import json
from pathlib import Path

from repromath.cli import run
from repromath.latex.compile import LatexCompileResult
from repromath.latex.parse_log import parse_latex_log_file
from repromath.latex.report import run_latex_qa


FIXTURES = Path(__file__).parent / "fixtures" / "latex_logs"


def test_parse_missing_references_citations_and_files() -> None:
    summary = parse_latex_log_file(FIXTURES / "missing_refs.log")

    assert summary.undefined_references == ["eq:hosvd-error-bound"]
    assert summary.undefined_citations == ["koldaBader2009"]
    assert summary.missing_files == [
        "thesis/figures/tensor_unfolding.pdf",
        "missing-package.sty",
    ]
    assert "Emergency stop." in summary.fatal_errors
    assert summary.output_pdf is None
    assert summary.page_count is None

    problems_by_kind = {problem.kind: problem for problem in summary.problems}
    assert problems_by_kind["undefined_reference"].severity == "error"
    assert problems_by_kind["undefined_reference"].line == 42
    assert problems_by_kind["undefined_citation"].severity == "error"
    assert problems_by_kind["missing_figure"].message == (
        "Missing figure file: `thesis/figures/tensor_unfolding.pdf`"
    )
    assert problems_by_kind["missing_file"].message == "Missing file: `missing-package.sty`"
    assert problems_by_kind["fatal_error"].severity == "fatal"


def test_parse_overfull_underfull_and_page_count() -> None:
    summary = parse_latex_log_file(FIXTURES / "overfull.log")

    assert summary.overfull_hbox_count == 2
    assert summary.underfull_hbox_count == 1
    assert summary.output_pdf == "main.pdf"
    assert summary.page_count == 7
    overfull_problems = [
        problem for problem in summary.problems if problem.kind == "overfull_hbox"
    ]
    assert len(overfull_problems) == 2
    assert overfull_problems[0].severity == "warning"
    assert overfull_problems[0].line == 10
    assert any(problem.kind == "underfull_hbox" for problem in summary.problems)
    assert any(problem.kind == "pdf_summary" for problem in summary.problems)


def test_parse_successful_log_has_pdf_summary_info_only() -> None:
    summary = parse_latex_log_file(FIXTURES / "success.log")

    assert not summary.has_problems
    assert summary.output_pdf == "clean.pdf"
    assert summary.page_count == 2
    assert [problem.kind for problem in summary.problems] == ["pdf_summary"]
    assert summary.problems[0].severity == "info"


def test_latex_qa_warning_only_log_reports_warn(
    tmp_path: Path,
    monkeypatch,
) -> None:
    project_root = tmp_path / "project"
    thesis_dir = project_root / "thesis"
    thesis_dir.mkdir(parents=True)
    (project_root / "repromath.toml").write_text("[project]\nname = \"x\"\n", encoding="utf-8")
    tex_path = thesis_dir / "main.tex"
    tex_path.write_text("\\documentclass{article}\\begin{document}x\\end{document}\n", encoding="utf-8")
    tex_path.with_suffix(".log").write_text(
        (FIXTURES / "overfull.log").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "repromath.latex.report.compile_with_latexmk",
        lambda _: LatexCompileResult(
            engine="latexmk",
            engine_path="/usr/bin/latexmk",
            attempted=True,
            returncode=0,
            stdout="",
            stderr="",
        ),
    )

    result = run_latex_qa(tex_path)

    assert result.status == "WARN"
    assert result.summary.overfull_hbox_count == 2
    assert result.summary.underfull_hbox_count == 1


def test_latex_qa_successful_log_reports_pass(
    tmp_path: Path,
    monkeypatch,
) -> None:
    project_root = tmp_path / "project"
    thesis_dir = project_root / "thesis"
    thesis_dir.mkdir(parents=True)
    (project_root / "repromath.toml").write_text("[project]\nname = \"x\"\n", encoding="utf-8")
    tex_path = thesis_dir / "main.tex"
    tex_path.write_text("\\documentclass{article}\\begin{document}x\\end{document}\n", encoding="utf-8")
    tex_path.with_suffix(".log").write_text(
        (FIXTURES / "success.log").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "repromath.latex.report.compile_with_latexmk",
        lambda _: LatexCompileResult(
            engine="latexmk",
            engine_path="/usr/bin/latexmk",
            attempted=True,
            returncode=0,
            stdout="",
            stderr="",
        ),
    )

    result = run_latex_qa(tex_path)

    assert result.status == "PASS"
    assert result.summary.output_pdf == "clean.pdf"
    assert result.summary.page_count == 2


def test_latex_qa_without_engine_parses_existing_log_and_writes_reports(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr("repromath.latex.compile.shutil.which", lambda _: None)
    project_root = tmp_path / "project"
    thesis_dir = project_root / "thesis"
    thesis_dir.mkdir(parents=True)
    (project_root / "repromath.toml").write_text("[project]\nname = \"x\"\n", encoding="utf-8")
    tex_path = thesis_dir / "main.tex"
    tex_path.write_text("\\documentclass{article}\\begin{document}x\\end{document}\n", encoding="utf-8")
    tex_path.with_suffix(".log").write_text(
        (FIXTURES / "missing_refs.log").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    result = run_latex_qa(tex_path)

    markdown_report = project_root / "reports" / "latex_qa.md"
    json_report = project_root / "reports" / "latex_qa.json"
    assert result.status == "FAIL"
    assert not result.compile_attempted
    assert markdown_report.is_file()
    assert json_report.is_file()
    assert "Undefined reference: `eq:hosvd-error-bound`" in markdown_report.read_text(
        encoding="utf-8"
    )
    assert "## Fatal Errors" in markdown_report.read_text(encoding="utf-8")
    assert "## Errors" in markdown_report.read_text(encoding="utf-8")
    data = json.loads(json_report.read_text(encoding="utf-8"))
    assert data["summary"]["undefined_citations"] == ["koldaBader2009"]
    assert data["problems"][0]["severity"] == "error"
    assert any(problem["kind"] == "missing_figure" for problem in data["problems"])


def test_cli_latex_qa_warning_only_log_exits_zero(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("repromath.latex.compile.shutil.which", lambda _: None)
    project_root = tmp_path / "project"
    thesis_dir = project_root / "thesis"
    thesis_dir.mkdir(parents=True)
    (project_root / "repromath.toml").write_text("[project]\nname = \"x\"\n", encoding="utf-8")
    tex_path = thesis_dir / "main.tex"
    tex_path.write_text("\\documentclass{article}\\begin{document}x\\end{document}\n", encoding="utf-8")
    tex_path.with_suffix(".log").write_text(
        (FIXTURES / "overfull.log").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    exit_code = run(["qa", "latex", str(tex_path)])

    assert exit_code == 0
    assert (project_root / "reports" / "latex_qa.md").is_file()
    assert (project_root / "reports" / "latex_qa.json").is_file()
    markdown = (project_root / "reports" / "latex_qa.md").read_text(encoding="utf-8")
    assert "Status: WARN" in markdown
    assert "## Warnings" in markdown
    assert "Overfull hbox: 12.0pt too wide" in markdown


def test_cli_latex_qa_error_log_exits_nonzero(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("repromath.latex.compile.shutil.which", lambda _: None)
    project_root = tmp_path / "project"
    thesis_dir = project_root / "thesis"
    thesis_dir.mkdir(parents=True)
    (project_root / "repromath.toml").write_text("[project]\nname = \"x\"\n", encoding="utf-8")
    tex_path = thesis_dir / "main.tex"
    tex_path.write_text("\\documentclass{article}\\begin{document}x\\end{document}\n", encoding="utf-8")
    tex_path.with_suffix(".log").write_text(
        (FIXTURES / "missing_refs.log").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    exit_code = run(["qa", "latex", str(tex_path)])

    assert exit_code == 1
    markdown = (project_root / "reports" / "latex_qa.md").read_text(encoding="utf-8")
    assert "Status: FAIL" in markdown
