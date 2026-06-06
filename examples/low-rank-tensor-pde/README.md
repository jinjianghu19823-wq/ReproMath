# Low-Rank Tensor PDE Showcase

This is a small dissertation-like showcase for ReproMath.

The narrative is:

> I used ReproMath to keep a low-rank tensor PDE dissertation project organized:
> theorem-study notebooks, tensor figures, numerical diagnostics, and LaTeX
> artifacts are checked and mapped.

The example is intentionally lightweight. It does not implement a full PDE
solver; it shows how a mathematical research project can move through:

```text
paper notes -> HOSVD notebook -> tensor figures -> LaTeX section -> QA reports
```

## Contents

- `notebooks/truncated-hosvd.ipynb`: a study-first notebook scaffold.
- `figures/tensor-unfolding.pdf`: conceptual tensor unfolding figure.
- `figures/singular-value-decay.pdf`: diagnostic singular value decay plot.
- `figures/storage-vs-rank.pdf`: storage comparison for Tucker-style ranks.
- `thesis/main.tex`: a small dissertation-like LaTeX file.
- `repromath.toml`: source-to-output mappings for the notebook and figures.

## Try It

From this directory:

```bash
repromath qa project
repromath qa latex thesis/main.tex
repromath qa notebook notebooks/truncated-hosvd.ipynb
```

Regenerate one of the figures in a fresh project with:

```bash
repromath scaffold figure tensor-unfolding
```
