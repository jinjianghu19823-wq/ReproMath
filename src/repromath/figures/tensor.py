"""Tensor concept figure recipe scripts."""

from __future__ import annotations


def tensor_fibers_script() -> str:
    return _script(
        r'''import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Line3DCollection


def cube_edges() -> list[list[tuple[float, float, float]]]:
    points = np.array([[x, y, z] for x in [0, 1] for y in [0, 1] for z in [0, 1]])
    edges = []
    for i, p in enumerate(points):
        for q in points[i + 1:]:
            if np.sum(np.abs(p - q)) == 1:
                edges.append([tuple(p), tuple(q)])
    return edges


def main() -> None:
    fig = plt.figure(figsize=(6.2, 5.0))
    axis = fig.add_subplot(111, projection="3d")
    axis.add_collection3d(Line3DCollection(cube_edges(), colors="#555555", linewidths=1.0))

    fibers = [
        ([(0.15, 0.25, 0.75), (0.95, 0.25, 0.75)], "#1f77b4", "mode-1 fiber"),
        ([(0.65, 0.05, 0.35), (0.65, 0.95, 0.35)], "#d62728", "mode-2 fiber"),
        ([(0.35, 0.75, 0.05), (0.35, 0.75, 0.95)], "#2ca02c", "mode-3 fiber"),
    ]
    for points, color, label in fibers:
        xs, ys, zs = zip(*points)
        axis.plot(xs, ys, zs, color=color, linewidth=4, label=label)

    axis.set_xlabel("mode 1")
    axis.set_ylabel("mode 2")
    axis.set_zlabel("mode 3")
    axis.set_title("Fibers of a third-order tensor")
    axis.legend(loc="upper left")
    axis.set_box_aspect((1, 1, 1))
    axis.view_init(elev=24, azim=-45)
    fig.savefig(Path(__file__).with_suffix(".pdf"), bbox_inches="tight")
'''
    )


def tensor_slices_script() -> str:
    return _script(
        r'''import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def draw_grid(axis, title: str, highlight: str) -> None:
    axis.set_title(title)
    axis.set_xlim(0, 4)
    axis.set_ylim(0, 4)
    axis.set_aspect("equal")
    axis.axis("off")
    for x in range(4):
        for y in range(4):
            face = "#e8eef7" if highlight == "all" else "white"
            axis.add_patch(Rectangle((x, y), 1, 1, facecolor=face, edgecolor="#666666"))
    axis.text(2, -0.45, "fixed one mode index", ha="center", fontsize=9)


def main() -> None:
    fig, axes = plt.subplots(1, 3, figsize=(8.2, 3.0), constrained_layout=True)
    draw_grid(axes[0], "frontal slice", "all")
    draw_grid(axes[1], "lateral slice", "all")
    draw_grid(axes[2], "horizontal slice", "all")
    fig.suptitle("Three common slices through a third-order tensor", y=1.08)
    fig.savefig(Path(__file__).with_suffix(".pdf"), bbox_inches="tight")
'''
    )


def tensor_unfolding_script() -> str:
    return _script(
        r'''import matplotlib.pyplot as plt
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
'''
    )


def _script(body: str) -> str:
    return f'''from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / ".matplotlib-cache"))

import matplotlib
matplotlib.use("Agg")
{body}


if __name__ == "__main__":
    main()
'''

