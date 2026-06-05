"""Reading-width layout helpers for review dashboards."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

# ~72ch at typical UI font size — comfortable for long review text.
DEFAULT_MAX_READING_WIDTH_PX = 680

# Side gutters when the viewport is wider than the reading column.
READING_WIDTH_GUTTER_RATIOS: tuple[int, int, int] = (3, 4, 3)


def main_column_width_fraction(ratios: tuple[int, int, int]) -> float:
    """Return the center column's share of horizontal space."""
    total = sum(ratios)
    if total <= 0:
        raise ValueError("ratios must sum to a positive integer")
    return ratios[1] / total


@contextmanager
def reading_width_column(
    st: Any,
    *,
    max_width_px: int = DEFAULT_MAX_READING_WIDTH_PX,
    gutter_ratios: tuple[int, int, int] = READING_WIDTH_GUTTER_RATIOS,
) -> Iterator[Any]:
    """Yield a centered column capped for long-form reading."""
    _left, main, _right = st.columns(list(gutter_ratios))
    with main:
        with st.container(width=max_width_px):
            yield main
