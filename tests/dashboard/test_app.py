"""Smoke tests for the Streamlit dashboard entry (mocked UI)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch


@patch("src.dashboard.app.st")
def test_main_renders_empty_shell(mock_st: MagicMock) -> None:
    """The dashboard loads with page config, title, and a single placeholder."""
    from src.dashboard.app import main

    main()

    mock_st.set_page_config.assert_called_once()
    mock_st.title.assert_called_once()
    mock_st.info.assert_called_once()
