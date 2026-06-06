"""Parse useful signals from LaTeX log files."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re


@dataclass(frozen=True)
class LatexLogSummary:
    undefined_references: list[str] = field(default_factory=list)
    undefined_citations: list[str] = field(default_factory=list)
    missing_files: list[str] = field(default_factory=list)
    overfull_hbox_count: int = 0
    underfull_hbox_count: int = 0
    fatal_errors: list[str] = field(default_factory=list)
    output_pdf: str | None = None
    page_count: int | None = None

    @property
    def has_problems(self) -> bool:
        return any(
            [
                self.undefined_references,
                self.undefined_citations,
                self.missing_files,
                self.overfull_hbox_count,
                self.underfull_hbox_count,
                self.fatal_errors,
            ]
        )


def parse_latex_log_file(log_path: Path) -> LatexLogSummary:
    return parse_latex_log(log_path.read_text(encoding="utf-8", errors="replace"))


def parse_latex_log(log_text: str) -> LatexLogSummary:
    undefined_references = _unique(
        re.findall(r"LaTeX Warning: Reference `([^']+)' .* undefined", log_text)
    )
    undefined_citations = _unique(
        re.findall(r"LaTeX Warning: Citation `([^']+)' .* undefined", log_text)
    )

    missing_files = _missing_files(log_text)

    fatal_errors = _fatal_errors(log_text)
    output_pdf, page_count = _output_pdf(log_text)

    return LatexLogSummary(
        undefined_references=undefined_references,
        undefined_citations=undefined_citations,
        missing_files=missing_files,
        overfull_hbox_count=log_text.count(r"Overfull \hbox"),
        underfull_hbox_count=log_text.count(r"Underfull \hbox"),
        fatal_errors=fatal_errors,
        output_pdf=output_pdf,
        page_count=page_count,
    )


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _missing_files(log_text: str) -> list[str]:
    patterns = [
        re.compile(r"! LaTeX Error: File `([^']+)' not found\."),
        re.compile(r"(?:LaTeX Warning|Package .*? Error): File `([^']+)' not found"),
    ]
    values: list[str] = []
    for line in log_text.splitlines():
        for pattern in patterns:
            match = pattern.search(line)
            if match is not None:
                values.append(match.group(1))
                break
    return _unique(values)


def _fatal_errors(log_text: str) -> list[str]:
    errors: list[str] = []
    for line in log_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("!"):
            errors.append(stripped)
        elif stripped in {"Emergency stop.", "Fatal error occurred, no output PDF file produced!"}:
            errors.append(stripped)
    return _unique(errors)[:20]


def _output_pdf(log_text: str) -> tuple[str | None, int | None]:
    match = re.search(
        r"Output written on (.+?) \((\d+) pages?,",
        log_text,
    )
    if match is None:
        return None, None
    return match.group(1), int(match.group(2))
