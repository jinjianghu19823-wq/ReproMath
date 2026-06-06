# Project Metadata

ReproMath projects use `repromath.toml`.

Minimal dissertation example:

```toml
[project]
name = "my-project"
type = "dissertation"
main_tex = "thesis/main.tex"

[paths]
notebooks = "notebooks"
figures = "figures"
reports = "reports"
sources = "sources"
```

Artifact mapping example:

```toml
[[artifacts]]
id = "fig_tensor_unfolding"
type = "figure"
output = "figures/tensor-unfolding.pdf"
source = "KoldaBader2009"
role = "conceptual illustration"
used_in = "thesis/sections/tensor_notation.tex"

[[artifacts]]
id = "notebook_truncated_hosvd"
type = "notebook"
output = "notebooks/truncated-hosvd.ipynb"
source = "DeLathauwer2000"
role = "toy implementation and diagnostics"
diagnostics = ["relative_error", "storage_ratio", "orthogonality_error"]
```

`repromath qa project` checks declared outputs, `used_in` files, LaTeX QA, and
declared notebook QA.

