"""Parse useful signals from LaTeX log files."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re


@dataclass(frozen=True)
class LatexProblem:
    severity: str
    kind: str
    message: str
    suggestion: str
    context: str | None = None
    line: int | None = None


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
    problems: list[LatexProblem] = field(default_factory=list)

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
    problems = _problems(log_text, output_pdf=output_pdf, page_count=page_count)

    return LatexLogSummary(
        undefined_references=undefined_references,
        undefined_citations=undefined_citations,
        missing_files=missing_files,
        overfull_hbox_count=log_text.count(r"Overfull \hbox"),
        underfull_hbox_count=log_text.count(r"Underfull \hbox"),
        fatal_errors=fatal_errors,
        output_pdf=output_pdf,
        page_count=page_count,
        problems=problems,
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


def _problems(
    log_text: str,
    output_pdf: str | None,
    page_count: int | None,
) -> list[LatexProblem]:
    problems: list[LatexProblem] = []
    for raw_line in log_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        reference_match = re.search(
            r"LaTeX Warning: Reference `([^']+)' .* undefined.* input line (\d+)",
            line,
        )
        if reference_match is not None:
            label = reference_match.group(1)
            problems.append(
                LatexProblem(
                    severity="error",
                    kind="undefined_reference",
                    message=f"Undefined reference: `{label}`",
                    suggestion=(
                        "Check whether the label is defined, misspelled, or needs "
                        "another LaTeX run to resolve."
                    ),
                    context=line,
                    line=int(reference_match.group(2)),
                )
            )
            continue

        citation_match = re.search(
            r"LaTeX Warning: Citation `([^']+)' .* undefined.* input line (\d+)",
            line,
        )
        if citation_match is not None:
            citation = citation_match.group(1)
            problems.append(
                LatexProblem(
                    severity="error",
                    kind="undefined_citation",
                    message=f"Missing citation: `{citation}`",
                    suggestion=(
                        "Check the bibliography database, citation key spelling, "
                        "and bibliography build step."
                    ),
                    context=line,
                    line=int(citation_match.group(2)),
                )
            )
            continue

        missing_file = _missing_file_from_line(line)
        if missing_file is not None:
            is_figure = _looks_like_figure(missing_file)
            problems.append(
                LatexProblem(
                    severity="error",
                    kind="missing_figure" if is_figure else "missing_file",
                    message=(
                        f"Missing figure file: `{missing_file}`"
                        if is_figure
                        else f"Missing file: `{missing_file}`"
                    ),
                    suggestion=(
                        "Check the figure path, file extension, and graphicspath."
                        if is_figure
                        else "Check package, bibliography, input, or file paths."
                    ),
                    context=line,
                )
            )
            continue

        overfull_match = re.search(
            r"Overfull \\hbox \(([^)]+)\).* lines? (\d+)(?:--(\d+))?",
            line,
        )
        if overfull_match is not None:
            problems.append(
                LatexProblem(
                    severity="warning",
                    kind="overfull_hbox",
                    message=f"Overfull hbox: {overfull_match.group(1)}",
                    suggestion=(
                        "Inspect the corresponding paragraph, displayed equation, "
                        "or long inline expression."
                    ),
                    context=line,
                    line=int(overfull_match.group(2)),
                )
            )
            continue

        underfull_match = re.search(
            r"Underfull \\hbox \(([^)]+)\).* lines? (\d+)(?:--(\d+))?",
            line,
        )
        if underfull_match is not None:
            problems.append(
                LatexProblem(
                    severity="warning",
                    kind="underfull_hbox",
                    message=f"Underfull hbox: {underfull_match.group(1)}",
                    suggestion=(
                        "Inspect the paragraph spacing or line break around this "
                        "location."
                    ),
                    context=line,
                    line=int(underfull_match.group(2)),
                )
            )
            continue

        if line in {"Emergency stop.", "Fatal error occurred, no output PDF file produced!"}:
            problems.append(
                LatexProblem(
                    severity="fatal",
                    kind="fatal_error",
                    message=line,
                    suggestion=(
                        "Fix the preceding LaTeX error first, then recompile from a "
                        "clean run."
                    ),
                    context=line,
                )
            )
            continue

        if line.startswith("!") and "File `" not in line:
            problems.append(
                LatexProblem(
                    severity="fatal",
                    kind="fatal_error",
                    message=line,
                    suggestion="Inspect the surrounding log context for the failing command.",
                    context=line,
                )
            )

    if output_pdf is not None:
        page_text = f" ({page_count} pages)" if page_count is not None else ""
        problems.append(
            LatexProblem(
                severity="info",
                kind="pdf_summary",
                message=f"PDF written: `{output_pdf}`{page_text}",
                suggestion="No action needed for this item.",
            )
        )
    return problems


def _missing_file_from_line(line: str) -> str | None:
    patterns = [
        re.compile(r"! LaTeX Error: File `([^']+)' not found\."),
        re.compile(r"(?:LaTeX Warning|Package .*? Error): File `([^']+)' not found"),
    ]
    for pattern in patterns:
        match = pattern.search(line)
        if match is not None:
            return match.group(1)
    return None


def _looks_like_figure(path: str) -> bool:
    lowered = path.lower()
    figure_extensions = (".pdf", ".png", ".jpg", ".jpeg", ".eps", ".svg")
    return lowered.endswith(figure_extensions) or "figure" in lowered


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
