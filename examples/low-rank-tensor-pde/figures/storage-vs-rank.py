from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / ".matplotlib-cache"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main() -> None:
    n1, n2, n3 = 50, 50, 50
    ranks = np.arange(1, 31)
    full_storage = np.full_like(ranks, n1 * n2 * n3)
    tucker_storage = ranks * (n1 + n2 + n3) + ranks ** 3

    fig, axis = plt.subplots(figsize=(6.4, 4.0), constrained_layout=True)
    axis.plot(ranks, full_storage, label="full tensor storage", linewidth=2)
    axis.plot(ranks, tucker_storage, label="Tucker storage", linewidth=2)
    axis.set_xlabel("equal Tucker rank r")
    axis.set_ylabel("number of stored scalars")
    axis.set_title("Full tensor storage vs Tucker storage")
    axis.legend()
    axis.grid(True, linewidth=0.5)
    fig.savefig(Path(__file__).with_suffix(".pdf"), bbox_inches="tight")


if __name__ == "__main__":
    main()
