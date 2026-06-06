# LaTeX QA

Run:

```bash
repromath qa latex thesis/main.tex
```

ReproMath looks for `latexmk`. If it is available, ReproMath compiles the file
in nonstop mode and then parses the `.log`. If `latexmk` is not available, it
parses an existing `.log` next to the `.tex` file when possible.

The report records:

- undefined references
- undefined citations
- missing files
- overfull and underfull hboxes
- fatal errors
- PDF production and parsed page count

Outputs:

```text
reports/latex_qa.md
reports/latex_qa.json
```

