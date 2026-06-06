from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / ".matplotlib-cache"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main() -> None:
    indices = np.arange(1, 41)
    fast_decay = np.exp(-0.18 * (indices - 1))
    slow_decay = 1 / (indices ** 1.4)

    fig, axis = plt.subplots(figsize=(6.2, 4.0), constrained_layout=True)
    axis.semilogy(indices, fast_decay, marker="o", markersize=3, label="fast decay")
    axis.semilogy(indices, slow_decay, marker="s", markersize=3, label="slow decay")
    axis.set_xlabel("index")
    axis.set_ylabel("singular value")
    axis.set_title("Toy singular value decay")
    axis.legend()
    axis.grid(True, which="both", linewidth=0.5)
    fig.savefig(Path(__file__).with_suffix(".pdf"), bbox_inches="tight")


if __name__ == "__main__":
    main()
