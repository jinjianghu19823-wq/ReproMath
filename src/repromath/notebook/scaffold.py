"""Create study-first mathematical research notebooks."""

from __future__ import annotations

from pathlib import Path
import re

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

from repromath.notebook.sections import REQUIRED_SECTIONS, section_metadata


class NotebookScaffoldError(Exception):
    """Raised when a notebook scaffold cannot be created safely."""


def create_notebook_scaffold(
    topic: str,
    base_dir: Path | None = None,
    output_path: Path | None = None,
) -> Path:
    if not topic.strip():
        raise NotebookScaffoldError("Notebook topic cannot be empty.")

    root = base_dir or Path.cwd()
    path = output_path or root / "notebooks" / f"{slugify(topic)}.ipynb"
    if not path.is_absolute():
        path = root / path
    path = path.resolve()

    if path.exists():
        raise NotebookScaffoldError(
            f"Refusing to overwrite existing notebook: {path}"
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    notebook = new_notebook(
        cells=_notebook_cells(topic),
        metadata={
            "repromath": {
                "topic": topic,
                "required_sections": list(REQUIRED_SECTIONS),
            },
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "pygments_lexer": "ipython3",
            },
        },
    )
    nbformat.write(notebook, path)
    return path


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "notebook"


def _notebook_cells(topic: str) -> list[nbformat.NotebookNode]:
    title = _title(topic)
    profile = _topic_profile(topic)
    cells: list[nbformat.NotebookNode] = [
        _markdown(
            "Title",
            f"""# {title}

This is a study-first ReproMath notebook. Its goal is to connect the mathematical idea, a small toy example, executable code, and diagnostic checks.
""",
        ),
        _markdown(
            "Motivation",
            profile["motivation"],
        ),
        _markdown(
            "Mathematical setup",
            profile["setup"],
        ),
        _markdown(
            "Definitions and notation",
            profile["definitions"],
        ),
        _markdown(
            "Algorithm",
            profile["algorithm"],
        ),
        _code(
            """import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["figure.figsize"] = (6, 4)
plt.rcParams["axes.grid"] = True
""",
        ),
        _code(
            """rng = np.random.default_rng(0)
""",
        ),
        _markdown(
            "Naive implementation",
            """Start with the simplest implementation that makes the mathematical structure visible. Keep this cell small, even if it is not the most stable approach.
""",
        ),
        _code(
            """# Placeholder for toy data.
# Replace this with a small example whose exact dimensions are easy to inspect.
A = rng.normal(size=(6, 4))
A.shape
""",
        ),
        _markdown(
            "Stable or recommended implementation",
            """Now write the version you would trust in a dissertation experiment. Use this section to avoid unstable shortcuts and to record the numerical reason for the recommended implementation.
""",
        ),
        _code(
            """# Placeholder for the recommended algorithm.
# Example: use SVD-based routines rather than forming normal equations.
U, singular_values, Vt = np.linalg.svd(A, full_matrices=False)
singular_values
""",
        ),
        _markdown(
            "Numerical experiment",
            """Run a small controlled experiment. Prefer one question, one parameter sweep, and a plot that makes the result checkable.
""",
        ),
        _code(
            """# Placeholder for a compact numerical experiment.
ranks = np.arange(1, min(A.shape) + 1)
errors = []
for rank in ranks:
    approximation = (U[:, :rank] * singular_values[:rank]) @ Vt[:rank, :]
    errors.append(np.linalg.norm(A - approximation) / np.linalg.norm(A))

plt.semilogy(ranks, errors, marker="o")
plt.xlabel("rank")
plt.ylabel("relative error")
plt.title("Approximation error by rank")
plt.show()
""",
        ),
        _markdown(
            "Diagnostics",
            """Record the quantities that tell you whether the computation is trustworthy: residuals, orthogonality error, condition numbers, storage ratios, or convergence rates.
""",
        ),
        _code(
            """# Placeholder for diagnostics.
orthogonality_error = np.linalg.norm(U.T @ U - np.eye(U.shape[1]))
relative_residual = errors[-1]

{
    "orthogonality_error": orthogonality_error,
    "relative_residual": relative_residual,
}
""",
        ),
        _markdown(
            "Interpretation",
            """Explain what the experiment shows in mathematical language. Say what changed, what stayed stable, and which diagnostic supports the claim.
""",
        ),
        _markdown(
            "Try it yourself",
            """Change the matrix dimensions, add noise, or replace the toy data with a structured example. Before trusting the result, predict which diagnostic should move and why.
""",
        ),
        _markdown(
            "References",
            """Add papers, lecture notes, books, or dissertation sections that justify the definitions and algorithms used in this notebook.
""",
        ),
    ]
    return cells


def _topic_profile(topic: str) -> dict[str, str]:
    normalized = topic.strip().lower().replace("-", " ")
    if "hosvd" in normalized:
        return {
            "motivation": """HOSVD is useful when matrix low-rank intuition has to be lifted to multiway data. The point of this notebook is to keep the tensor notation, mode unfoldings, truncation rule, and diagnostics in one reproducible place.
""",
            "setup": """Let a tensor be represented by an array with three or more modes. The main objects to track are mode-n unfoldings, factor matrices, a core tensor, and an approximation rank for each mode.
""",
            "definitions": """Write down the tensor dimensions, mode indices, unfoldings, factor matrices, Tucker core, truncation ranks, and the norm used to measure approximation error.
""",
            "algorithm": """The HOSVD pattern is: unfold the tensor along each mode, compute singular vectors of each unfolding, project the tensor into the factor spaces, then reconstruct from the truncated core and factors.
""",
        }
    if "svd" in normalized:
        return {
            "motivation": """SVD is the smallest useful laboratory for low-rank approximation. It lets you see singular value decay, truncation error, orthogonality, and storage tradeoffs before moving to tensor methods.
""",
            "setup": """Let A be a rectangular matrix. The experiment should track its singular values, rank-r approximations, residuals, and orthogonality of computed singular vectors.
""",
            "definitions": """Define the SVD A = U Sigma V^T, the truncated rank-r approximation, the norm used for error, and the diagnostic quantities that decide whether the computation is stable.
""",
            "algorithm": """Compute the SVD, choose a rank, reconstruct the rank-r approximation, and compare the residual against the singular value tail.
""",
        }
    return {
        "motivation": f"""Use this notebook to turn the topic "{topic}" into a reproducible mathematical study: motivation, definitions, implementation, experiment, diagnostics, and interpretation.
""",
        "setup": """State the mathematical objects, dimensions, assumptions, and the smallest toy example that still shows the core phenomenon.
""",
        "definitions": """List the notation carefully. Include domains, norms, parameters, and any diagnostic quantities that will be computed later.
""",
        "algorithm": """Describe the algorithm in steps before coding it. Separate the naive version from the stable or recommended version.
""",
    }


def _title(topic: str) -> str:
    small_words = {"and", "or", "the", "of", "vs"}
    words = []
    for word in topic.strip().split():
        upper = word.upper()
        if upper in {"SVD", "HOSVD", "PDE"}:
            words.append(upper)
        elif word.lower() in small_words:
            words.append(word.lower())
        else:
            words.append(word[:1].upper() + word[1:])
    return " ".join(words)


def _markdown(section: str, source: str) -> nbformat.NotebookNode:
    if section != "Title":
        source = f"## {section}\n\n{source.strip()}\n"
    cell = new_markdown_cell(source=source.strip() + "\n")
    cell.metadata.update(section_metadata(section))
    return cell


def _code(source: str) -> nbformat.NotebookNode:
    return new_code_cell(source=source.strip() + "\n")

