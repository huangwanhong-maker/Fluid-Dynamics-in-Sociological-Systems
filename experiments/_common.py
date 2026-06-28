"""Shared plotting helpers for the figure gallery."""

from __future__ import annotations

import os

ASSETS = "assets"


def get_plt():
    """Return a headless matplotlib.pyplot, or None if unavailable."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        return plt
    except Exception as exc:  # pragma: no cover
        print(f"(matplotlib unavailable: {exc})")
        return None


def save(fig, name: str) -> str:
    """Save a figure into the assets folder and return its path."""
    os.makedirs(ASSETS, exist_ok=True)
    path = os.path.join(ASSETS, name)
    fig.savefig(path, dpi=120, bbox_inches="tight")
    print(f"  saved {path}")
    return path
