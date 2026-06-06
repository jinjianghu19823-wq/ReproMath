from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / ".matplotlib-cache"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle


def main() -> None:
    fig, axis = plt.subplots(figsize=(7.4, 3.4))
    axis.axis("off")
    axis.set_xlim(0, 10)
    axis.set_ylim(0, 5)

    offsets = [(0.8, 1.0), (1.15, 1.35), (1.5, 1.7)]
    for index, (x, y) in enumerate(offsets):
        axis.add_patch(Rectangle((x, y), 2.2, 1.7, facecolor="#e8eef7", edgecolor="#555555"))
        axis.text(x + 1.1, y + 0.85, f"slice {index + 1}", ha="center", va="center", fontsize=9)
    axis.text(1.9, 0.35, "3D tensor", ha="center", fontsize=10)

    axis.add_patch(FancyArrowPatch((4.1, 2.4), (5.9, 2.4), arrowstyle="->", mutation_scale=18))
    axis.text(5.0, 2.7, "mode-n unfolding", ha="center", fontsize=10)

    axis.add_patch(Rectangle((6.2, 1.1), 3.0, 2.6, facecolor="#f7f7f7", edgecolor="#555555"))
    for x in [7.2, 8.2]:
        axis.plot([x, x], [1.1, 3.7], color="#777777", linewidth=0.8)
    for y in [1.75, 2.4, 3.05]:
        axis.plot([6.2, 9.2], [y, y], color="#777777", linewidth=0.8)
    axis.text(7.7, 0.35, "mode-n matrix", ha="center", fontsize=10)
    axis.set_title("Tensor unfolding maps multiway data into a matrix view")
    fig.savefig(Path(__file__).with_suffix(".pdf"), bbox_inches="tight")



if __name__ == "__main__":
    main()
