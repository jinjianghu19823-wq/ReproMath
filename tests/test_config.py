from __future__ import annotations

from pathlib import Path

from repromath.config import load_project_config


def test_load_project_config_with_artifacts(tmp_path: Path) -> None:
    config_path = tmp_path / "repromath.toml"
    config_path.write_text(
        """
[project]
name = "demo"
type = "dissertation"
main_tex = "thesis/main.tex"

[paths]
reports = "reports"

[[artifacts]]
id = "fig_tensor_unfolding"
type = "figure"
output = "figures/tensor_unfolding.pdf"
source = "KoldaBader2009"
role = "conceptual illustration"
used_in = "thesis/sections/tensor_notation.tex"
diagnostics = ["relative_error"]
""",
        encoding="utf-8",
    )

    config = load_project_config(tmp_path)

    assert config.name == "demo"
    assert config.project_type == "dissertation"
    assert config.main_tex == "thesis/main.tex"
    assert config.paths["reports"] == "reports"
    assert len(config.artifacts) == 1
    artifact = config.artifacts[0]
    assert artifact.id == "fig_tensor_unfolding"
    assert artifact.artifact_type == "figure"
    assert artifact.output == "figures/tensor_unfolding.pdf"
    assert artifact.diagnostics == ["relative_error"]

