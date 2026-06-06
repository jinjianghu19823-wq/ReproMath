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

The report also records a compact notebook summary:

* total, Markdown, and code cell counts;
* cells with saved outputs;
* cells with `execution_count`;
* required section status;
* random seed status;
* conservative stale-output warnings.

When `--execute` is used, the Markdown and JSON reports include execution
runtime, pass/fail status, the first failing zero-based cell index when
available, and a short error name/message.

Outputs:

```text
reports/notebook_qa.md
reports/notebook_qa.json
```

The JSON report includes `schema_version` and `tool_version` fields so external
scripts can check the report format before consuming it.
