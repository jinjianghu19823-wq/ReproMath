# Figure Recipes

Run:

```bash
repromath scaffold figure tensor-unfolding
```

Each recipe creates:

- `figures/<recipe>.py`
- `figures/<recipe>.pdf`
- `figures/<recipe>.md`

Supported recipes:

- `svd-rank-one`
- `tensor-fibers`
- `tensor-slices`
- `tensor-unfolding`
- `singular-value-decay`
- `storage-vs-rank`

The scripts use Matplotlib with the non-interactive `Agg` backend so they can
run in CI and terminal-only environments.

