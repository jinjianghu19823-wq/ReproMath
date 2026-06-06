# Quickstart

Install locally:

```bash
python -m pip install -e ".[dev]"
repromath --version
```

Create a dissertation project:

```bash
repromath init dissertation my-project
cd my-project
```

Create a notebook and a figure:

```bash
repromath scaffold notebook --topic "truncated HOSVD"
repromath scaffold figure tensor-unfolding
```

Run QA:

```bash
repromath qa latex thesis/main.tex
repromath qa notebook notebooks/truncated-hosvd.ipynb
repromath qa project
```

Reports are written to `reports/` as Markdown and JSON.

