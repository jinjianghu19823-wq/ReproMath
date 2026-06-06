# ReproMath

ReproMath is a CLI toolkit for reproducible mathematical research projects.
It helps students and researchers turn mathematical study into clean,
checkable artifacts: structured notebooks, dissertation-ready figures,
LaTeX/PDF QA reports, notebook execution checks, and lightweight
source-to-output provenance.

It is for people working with mathematical papers, lecture notes, Jupyter
notebooks, numerical experiments, and LaTeX reports. It is especially useful
for numerical analysis, scientific computing, applied mathematics, and
computational mathematics projects where a result often moves through several
forms:

```text
paper -> theorem notes -> toy example -> notebook -> figure -> LaTeX section -> final PDF
```

ReproMath is not a notebook environment, a publishing system, a LaTeX engine,
a theorem prover, a workflow engine, or a generic AI wrapper.

## Why This Exists

Mathematical research rarely lives in one file. A result often starts as a
paper margin note, becomes a toy notebook, turns into a diagnostic figure,
then lands in a LaTeX section and final PDF. ReproMath gives that path a thin
layer of structure and QA without replacing the tools researchers already use.

```text
paper/theorem
    -> study notebook
    -> diagnostic figure
    -> LaTeX section
    -> QA reports
    -> final PDF
```

## Install

For local development:

```bash
python -m pip install -e ".[dev]"
repromath --version
```

Expected version:

```text
repromath 0.1.0
```

You can also run the CLI without installing:

```bash
PYTHONPATH=src python -m repromath.cli --version
```

## 60-Second Demo

```bash
repromath init dissertation demo-dissertation
cd demo-dissertation

repromath scaffold notebook --topic "truncated HOSVD"
repromath scaffold figure tensor-unfolding

repromath qa latex thesis/main.tex
repromath qa notebook notebooks/truncated-hosvd.ipynb
repromath qa project
```

After those commands, inspect:

```text
reports/latex_qa.md
reports/notebook_qa.md
reports/project_qa.md
```

## Quickstart

Create a dissertation-style project:

```bash
repromath init dissertation my-project
cd my-project
```

Create a study-first notebook:

```bash
repromath scaffold notebook --topic "truncated HOSVD"
```

Create a dissertation-friendly figure:

```bash
repromath scaffold figure tensor-unfolding
```

Run QA checks:

```bash
repromath qa latex thesis/main.tex
repromath qa notebook notebooks/truncated-hosvd.ipynb
repromath qa project
```

## Commands

```bash
repromath --version
repromath init dissertation my-project
repromath init paper-study my-paper-study
repromath init numerical-experiment my-experiment
repromath qa latex thesis/main.tex
repromath qa notebook notebooks/example.ipynb
repromath qa notebook notebooks/example.ipynb --execute
repromath qa project
repromath scaffold notebook --topic "truncated HOSVD"
repromath scaffold figure tensor-unfolding
```

Supported figure recipes:

- `svd-rank-one`
- `tensor-fibers`
- `tensor-slices`
- `tensor-unfolding`
- `singular-value-decay`
- `storage-vs-rank`

## Example Report Snippets

LaTeX QA:

```text
# LaTeX QA Report

Status: PASS

PDF produced: yes
Page count: 1
```

Project QA:

```text
# Project QA Report

Status: PASS

LaTeX QA: PASS
Notebook QA: PASS
Missing Files: None
```

## Showcase

The first public showcase is
[Showcase: Low-Rank Tensor PDE](docs/showcase-low-rank-tensor-pde.md).

It demonstrates a small dissertation workflow with a truncated HOSVD notebook,
tensor figures, LaTeX sections, `repromath.toml` provenance mappings, and
example QA reports. A new user can read the showcase first to see the value of
ReproMath before creating a fresh project.

Try it after installing ReproMath:

```bash
cd examples/low-rank-tensor-pde
repromath qa project
```

## Documentation

- [Quickstart](docs/quickstart.md)
- [CLI reference](docs/cli-reference.md)
- [LaTeX QA](docs/latex-qa.md)
- [Notebook scaffold](docs/notebook-scaffold.md)
- [Notebook QA](docs/notebook-qa.md)
- [Figure recipes](docs/figure-recipes.md)
- [Project metadata](docs/project-metadata.md)
- [Showcase: Low-rank tensor PDE](docs/showcase-low-rank-tensor-pde.md)
- [Release checklist](docs/release-checklist.md)
- [Contributing](docs/contributing.md)

## License

MIT.
