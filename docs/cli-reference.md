# CLI Reference

## Version

```bash
repromath --version
```

## Project Initialization

```bash
repromath init dissertation PROJECT_NAME
repromath init paper-study PROJECT_NAME
repromath init numerical-experiment PROJECT_NAME
```

The command refuses to overwrite an existing project directory.

## QA

```bash
repromath qa latex PATH_TO_TEX
repromath qa notebook PATH_TO_IPYNB
repromath qa notebook PATH_TO_IPYNB --execute
repromath qa project
```

## Scaffolding

```bash
repromath scaffold notebook --topic "truncated HOSVD"
repromath scaffold figure tensor-unfolding
```

Figure recipes are `svd-rank-one`, `tensor-fibers`, `tensor-slices`,
`tensor-unfolding`, `singular-value-decay`, and `storage-vs-rank`.

