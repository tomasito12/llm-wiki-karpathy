"""Tests for reading-width layout helpers."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.ingest_review.layout_ui import (
    DEFAULT_MAX_READING_WIDTH_PX,
    READING_WIDTH_GUTTER_RATIOS,
    main_column_width_fraction,
    reading_width_column,
)


def test_main_column_width_fraction_default_ratios() -> None:
    assert main_column_width_fraction(READING_WIDTH_GUTTER_RATIOS) == pytest.approx(0.4)


def test_main_column_width_fraction_custom_ratios() -> None:
    assert main_column_width_fraction((1, 2, 1)) == pytest.approx(0.5)


def test_main_column_width_fraction_rejects_empty_sum() -> None:
    with pytest.raises(ValueError, match="positive integer"):
        main_column_width_fraction((0, 0, 0))


def test_reading_width_column_uses_centered_gutters_and_capped_container() -> None:
    st = MagicMock()
    main_col = MagicMock()
    st.columns.return_value = (MagicMock(), main_col, MagicMock())

    with reading_width_column(st) as yielded:
        assert yielded is main_col

    st.columns.assert_called_once_with(list(READING_WIDTH_GUTTER_RATIOS))
    st.container.assert_called_once_with(width=DEFAULT_MAX_READING_WIDTH_PX)
