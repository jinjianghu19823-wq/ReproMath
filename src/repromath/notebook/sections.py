"""Standard notebook sections used by ReproMath."""

from __future__ import annotations

REQUIRED_SECTIONS: tuple[str, ...] = (
    "Title",
    "Motivation",
    "Mathematical setup",
    "Definitions and notation",
    "Algorithm",
    "Naive implementation",
    "Stable or recommended implementation",
    "Numerical experiment",
    "Diagnostics",
    "Interpretation",
    "Try it yourself",
    "References",
)


def section_metadata(section: str) -> dict[str, str]:
    return {"repromath_section": section}

