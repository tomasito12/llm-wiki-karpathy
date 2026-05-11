"""Smoke tests for the Streamlit dashboard entry (mocked UI)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

REPO_ROOT = Path(__file__).resolve().parents[2]


@patch("src.dashboard.app.list_readwise_html_sources", return_value=[])
@patch("src.dashboard.app.load_repo_dotenv", return_value=REPO_ROOT)
@patch("src.dashboard.app.st")
def test_main_handles_empty_raw_dir(
    mock_st: MagicMock, _mock_load_repo: MagicMock, _mock_list: MagicMock
) -> None:
    """The dashboard loads and exits early when no HTML sources exist."""
    mock_st.sidebar.__enter__ = MagicMock(return_value=mock_st.sidebar)
    mock_st.sidebar.__exit__ = MagicMock(return_value=False)
    from src.dashboard.app import main

    main()

    mock_st.set_page_config.assert_called_once()
    mock_st.title.assert_called_once()
    mock_st.info.assert_called_once()
