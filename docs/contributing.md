# Contributing

ReproMath should stay a thin workflow layer for mathematical research projects.

Guidelines:

- Prefer small, reviewable changes.
- Keep code deterministic and explicit.
- Do not turn ReproMath into a generic AI wrapper.
- Do not replace Jupyter, Quarto, LaTeX, latexmk, nbQA, Snakemake, DVC, or Cookiecutter.
- Add tests for CLI behavior and generated artifacts.
- Run `python -m pytest` before opening a pull request.

For larger ideas, start with a small explicit version and document the tradeoff
before adding abstraction.

