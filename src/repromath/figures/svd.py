"""SVD-related figure recipe scripts."""

from __future__ import annotations


def svd_rank_one_script() -> str:
    return r'''from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / ".matplotlib-cache"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main() -> None:
    rng = np.random.default_rng(4)
    u1 = np.linspace(1.0, 0.2, 6)
    v1 = np.linspace(0.2, 1.0, 5)
    u2 = rng.normal(size=6)
    v2 = rng.normal(size=5)

    rank_one_a = np.outer(u1, v1)
    rank_one_b = 0.28 * np.outer(u2, v2)
    matrix = rank_one_a + rank_one_b

    fig, axes = plt.subplots(1, 3, figsize=(8.5, 3.0), constrained_layout=True)
    panels = [
        (matrix, "matrix A"),
        (rank_one_a, "rank-one term 1"),
        (rank_one_b, "rank-one term 2"),
    ]
    limits = (matrix.min(), matrix.max())
    for axis, (data, title) in zip(axes, panels):
        image = axis.imshow(data, cmap="viridis", vmin=limits[0], vmax=limits[1])
        axis.set_title(title)
        axis.set_xticks([])
        axis.set_yticks([])
    fig.colorbar(image, ax=axes, shrink=0.78, label="entry value")
    fig.suptitle("A small matrix as a sum of rank-one outer products", y=1.04)
    fig.savefig(Path(__file__).with_suffix(".pdf"), bbox_inches="tight")


if __name__ == "__main__":
    main()
'''

