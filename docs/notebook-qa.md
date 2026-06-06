# Notebook QA

Run structural QA:

```bash
repromath qa notebook notebooks/truncated-hosvd.ipynb
```

Run structural QA plus execution:

```bash
repromath qa notebook notebooks/truncated-hosvd.ipynb --execute
```

The structural check verifies that required study-first sections exist, code
cells are present, and a random seed appears. Execution is optional because
research notebooks may be slow or require local data.

Outputs:

```text
reports/notebook_qa.md
reports/notebook_qa.json
```

