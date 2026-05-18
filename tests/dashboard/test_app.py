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
    mock_st.radio.return_value = "Ingest review"
    mock_st.sidebar.__enter__ = MagicMock(return_value=mock_st.sidebar)
    mock_st.sidebar.__exit__ = MagicMock(return_value=False)
    from src.dashboard.app import main

    main()

    mock_st.set_page_config.assert_called_once()
    mock_st.title.assert_called_once()
    mock_st.info.assert_called_once()


@patch("src.dashboard.tag_registry_ui.render_tag_registry")
@patch("src.dashboard.app.load_repo_dotenv", return_value=REPO_ROOT)
@patch("src.dashboard.app.st")
def test_main_tag_registry_view_short_circuits_ingest(
    mock_st: MagicMock,
    _mock_load_repo: MagicMock,
    mock_render_registry: MagicMock,
) -> None:
    """Tag registry view renders registry UI and skips ingest review."""
    mock_st.radio.return_value = "Tag registry"
    mock_st.sidebar.__enter__ = MagicMock(return_value=mock_st.sidebar)
    mock_st.sidebar.__exit__ = MagicMock(return_value=False)
    from src.dashboard.app import main

    main()

    mock_render_registry.assert_called_once()
    mock_st.title.assert_called_with("Tag registry")


@patch("src.dashboard.app._collect_and_persist_tags")
@patch("src.dashboard.app.record_review_session")
@patch("src.dashboard.app.record_events_from_artifact")
@patch("src.dashboard.app.save_artifact")
@patch("src.dashboard.app.default_feedback_db_path", return_value=Path("/tmp/feedback.db"))
def test_finish_review_session_sets_finished_at_without_prior_timer(
    _mock_fb_path: MagicMock,
    mock_save: MagicMock,
    _mock_events: MagicMock,
    _mock_session: MagicMock,
    _mock_tags: MagicMock,
) -> None:
    """Finish must mark the review finished even if the timer widget never ran."""
    artifact: dict = {"review_analytics": {}, "review": {}}
    mock_st = MagicMock()
    root = REPO_ROOT
    artifact_path = root / "state" / "reviews" / "src-1" / "review.json"

    from src.dashboard.app import finish_review_session

    msg = finish_review_session(mock_st, artifact, artifact_path, root)

    finished = artifact["review_analytics"].get("review_finished_at")
    assert isinstance(finished, str) and finished.strip()
    assert "Review finished" in msg
    mock_save.assert_called_once_with(artifact_path, artifact)
