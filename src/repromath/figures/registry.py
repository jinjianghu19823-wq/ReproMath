"""Registry for built-in figure recipes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from repromath.figures.convergence import singular_value_decay_script
from repromath.figures.storage import storage_vs_rank_script
from repromath.figures.svd import svd_rank_one_script
from repromath.figures.tensor import (
    tensor_fibers_script,
    tensor_slices_script,
    tensor_unfolding_script,
)


@dataclass(frozen=True)
class FigureRecipe:
    name: str
    description: str
    script_factory: Callable[[], str]


FIGURE_RECIPES: dict[str, FigureRecipe] = {
    "svd-rank-one": FigureRecipe(
        name="svd-rank-one",
        description="Visualize a matrix as a sum of rank-one outer products.",
        script_factory=svd_rank_one_script,
    ),
    "tensor-fibers": FigureRecipe(
        name="tensor-fibers",
        description="Show mode-1, mode-2, and mode-3 fibers in a tensor cube.",
        script_factory=tensor_fibers_script,
    ),
    "tensor-slices": FigureRecipe(
        name="tensor-slices",
        description="Show frontal, lateral, and horizontal tensor slices.",
        script_factory=tensor_slices_script,
    ),
    "tensor-unfolding": FigureRecipe(
        name="tensor-unfolding",
        description="Show the idea of mapping a tensor into a mode-n matrix unfolding.",
        script_factory=tensor_unfolding_script,
    ),
    "singular-value-decay": FigureRecipe(
        name="singular-value-decay",
        description="Plot toy singular values with fast and slow decay.",
        script_factory=singular_value_decay_script,
    ),
    "storage-vs-rank": FigureRecipe(
        name="storage-vs-rank",
        description="Compare full tensor storage against Tucker storage by rank.",
        script_factory=storage_vs_rank_script,
    ),
}
