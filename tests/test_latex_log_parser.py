from __future__ import annotations

import json
from pathlib import Path

from repromath.cli import run
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


def test_parse_overfull_underfull_and_page_count() -> None:
    summary = parse_latex_log_file(FIXTURES / "overfull.log")

    assert summary.overfull_hbox_count == 2
    assert summary.underfull_hbox_count == 1
    assert summary.output_pdf == "main.pdf"
    assert summary.page_count == 7


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
    data = json.loads(json_report.read_text(encoding="utf-8"))
    assert data["summary"]["undefined_citations"] == ["koldaBader2009"]


def test_cli_latex_qa_writes_reports(tmp_path: Path, monkeypatch) -> None:
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

    assert exit_code == 1
    assert (project_root / "reports" / "latex_qa.md").is_file()
    assert (project_root / "reports" / "latex_qa.json").is_file()
