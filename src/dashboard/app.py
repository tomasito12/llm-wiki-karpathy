"""Streamlit placeholder for a future ingest GUI with human approval."""

from __future__ import annotations

import streamlit as st


def main() -> None:
    """Render an empty dashboard shell (no ingest widgets yet)."""
    st.set_page_config(
        page_title="LLM Wiki — ingest",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.title("LLM Wiki — ingest")
    st.info("Empty shell — ingest controls will be added here.")


if __name__ == "__main__":
    main()
