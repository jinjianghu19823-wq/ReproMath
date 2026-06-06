"""LaTeX compilation helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess


@dataclass(frozen=True)
class LatexCompileResult:
    engine: str
    engine_path: str | None
    attempted: bool
    returncode: int | None
    stdout: str
    stderr: str


def compile_with_latexmk(tex_path: Path) -> LatexCompileResult:
    """Compile a TeX file with latexmk when it is available."""

    engine_path = shutil.which("latexmk")
    if engine_path is None:
        return LatexCompileResult(
            engine="latexmk",
            engine_path=None,
            attempted=False,
            returncode=None,
            stdout="",
            stderr="latexmk was not found on PATH.",
        )

    completed = subprocess.run(
        [
            engine_path,
            "-pdf",
            "-interaction=nonstopmode",
            "-halt-on-error",
            tex_path.name,
        ],
        cwd=tex_path.parent,
        check=False,
        capture_output=True,
        text=True,
    )
    return LatexCompileResult(
        engine="latexmk",
        engine_path=engine_path,
        attempted=True,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )

