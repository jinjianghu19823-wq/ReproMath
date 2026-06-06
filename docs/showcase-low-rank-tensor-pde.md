# Showcase: Low-Rank Tensor PDE

This showcase is a small dissertation-style ReproMath project:

```text
examples/low-rank-tensor-pde
```

It is not a PDE solver. It is a checkable workflow example for the path a
mathematical research idea often takes:

```text
paper/theorem study -> HOSVD notebook -> tensor figures -> LaTeX section -> QA reports
```

The example uses low-rank tensor language because it gives a compact way to
show notebooks, figures, LaTeX writing, and provenance mappings in one place.
The same pattern is meant to apply to numerical analysis, scientific computing,
and applied mathematics projects more broadly.

## What It Contains

```text
examples/low-rank-tensor-pde/
  repromath.toml
  notebooks/truncated-hosvd.ipynb
  figures/tensor-unfolding.pdf
  figures/singular-value-decay.pdf
  figures/storage-vs-rank.pdf
  thesis/main.tex
  thesis/sections/tensor_notation.tex
  thesis/sections/numerical_diagnostics.tex
  reports/project_qa.md
  reports/latex_qa.md
  reports/notebook_qa.md
```

The intended story is:

1. A paper/theorem study motivates a truncated HOSVD notebook.
2. The notebook keeps the toy implementation and diagnostics in one place.
3. Figure recipes create dissertation-ready tensor and diagnostic figures.
4. LaTeX sections use those figures.
5. ReproMath QA reports check the project, LaTeX output, and notebook structure.

## Try It

From the repository root:

```bash
cd examples/low-rank-tensor-pde
repromath qa project
repromath qa latex thesis/main.tex
repromath qa notebook notebooks/truncated-hosvd.ipynb
```

After running the commands, inspect:

```text
reports/project_qa.md
reports/latex_qa.md
reports/notebook_qa.md
```

## Project QA Snippet

`repromath qa project` shows the declared research artifacts as a table:

```text
Status: PASS

| id | type | output | output_exists | source | used_in | used_in_exists | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| notebook_truncated_hosvd | notebook | notebooks/truncated-hosvd.ipynb | yes | DeLathauwer2000 | - | - | PASS |
| fig_tensor_unfolding | figure | figures/tensor-unfolding.pdf | yes | KoldaBader2009 | thesis/sections/tensor_notation.tex | yes | PASS |
```

It also summarizes source coverage:

```text
Artifacts: 4
Artifacts with source: 4
Artifacts with used_in: 3
Missing outputs: 0
Missing used_in files: 0
```

## LaTeX QA Snippet

`repromath qa latex thesis/main.tex` confirms that the dissertation draft builds:

```text
Status: PASS
PDF produced: yes
Page count: 3
No problems found in the parsed LaTeX log.
```

## Notebook QA Snippet

`repromath qa notebook notebooks/truncated-hosvd.ipynb` checks the notebook as a
research artifact:

```text
Status: PASS
Total cells: 18
Markdown cells: 12
Code cells: 6
Required sections found: 12 / 12
Random seed found: yes
Stale output warning: no
```

## Why repromath.toml Matters

The `repromath.toml` file records lightweight source-to-output mappings:

```toml
[[artifacts]]
id = "fig_tensor_unfolding"
type = "figure"
output = "figures/tensor-unfolding.pdf"
source = "KoldaBader2009"
role = "conceptual illustration"
used_in = "thesis/sections/tensor_notation.tex"
```

That mapping lets project QA answer practical questions:

* Does the declared output exist?
* Is the figure or notebook tied back to a source?
* Is the output used in a LaTeX section or other downstream file?
* Are any declared downstream files missing?

ReproMath does not rebuild the artifact graph. It keeps the graph visible and
checkable so a researcher can see which files support the final PDF.
