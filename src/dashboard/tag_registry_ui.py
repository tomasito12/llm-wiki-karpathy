"""Streamlit UI for editing ingestion-review tag/type allowlist YAML files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as streamlit_runtime

from src.ingest_review.tag_registry import TAG_TAXONOMIES, TagTaxonomySpec, taxonomy_by_id
from src.ingest_review.tags import (
    add_tags_to_list,
    find_similar_tags,
    load_tag_list,
    parse_comma_separated_tags,
    remove_tags_from_list,
    rename_tag_in_list,
)
from src.wiki_reset.tag_taxonomy import write_tag_taxonomy_file

_TAXONOMY_LABELS: dict[str, str] = {spec.id: spec.label for spec in TAG_TAXONOMIES}
_TAXONOMY_IDS: list[str] = [spec.id for spec in TAG_TAXONOMIES]


def _resolve_spec(taxonomy_id: str) -> TagTaxonomySpec:
    spec = taxonomy_by_id(taxonomy_id)
    if spec is None:
        return TAG_TAXONOMIES[0]
    return spec


def _taxonomy_path(spec: TagTaxonomySpec, root: Path) -> Path:
    return spec.path_fn(root)


def render_tag_registry(st: Any, *, root: Path) -> None:
    """Browse and edit allowlist YAML files under ``config/``."""
    st.caption(
        "Edit routing tags and tool/model type registries. "
        "Renames and removals update YAML only — saved review artifacts keep old slugs."
    )

    if "tag_registry_taxonomy_id" not in streamlit_runtime.session_state:
        streamlit_runtime.session_state["tag_registry_taxonomy_id"] = _TAXONOMY_IDS[0]
    elif streamlit_runtime.session_state["tag_registry_taxonomy_id"] not in _TAXONOMY_IDS:
        streamlit_runtime.session_state["tag_registry_taxonomy_id"] = _TAXONOMY_IDS[0]

    taxonomy_id = st.selectbox(
        "Allowlist",
        options=_TAXONOMY_IDS,
        format_func=lambda tid: _TAXONOMY_LABELS.get(tid, tid),
        key="tag_registry_taxonomy_id",
    )
    spec = _resolve_spec(taxonomy_id)
    path = _taxonomy_path(spec, root)
    rel_path = path.relative_to(root).as_posix() if path.is_relative_to(root) else str(path)

    st.markdown(f"**File:** `{rel_path}`")
    if spec.description:
        st.caption(spec.description)

    tags = load_tag_list(path)
    st.metric("Tags on allowlist", len(tags))

    if tags:
        st.dataframe(
            {"tag": tags},
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("This allowlist is empty.")

    st.divider()
    st.markdown("#### Add tags")
    add_key = f"tag_registry_add_{taxonomy_id}"
    if add_key not in streamlit_runtime.session_state:
        streamlit_runtime.session_state[add_key] = ""
    add_raw = st.text_input(
        "Comma-separated slugs",
        key=add_key,
        placeholder="e.g. agentic-ai, knowledge-management",
        help="Kebab-case slugs are normalized on save.",
    )
    if st.button("Add tags", key=f"tag_registry_add_btn_{taxonomy_id}", type="primary"):
        to_add = parse_comma_separated_tags(add_raw)
        if not to_add:
            st.warning("Enter at least one tag slug.")
        else:
            for slug in to_add:
                similar = find_similar_tags(slug, tags)
                if similar:
                    st.warning(
                        f"`{slug}` is similar to existing: "
                        + ", ".join(f"`{s}`" for s in similar[:3])
                    )
            added = add_tags_to_list(path, to_add)
            if added:
                st.success("Added: " + ", ".join(f"`{t}`" for t in added))
                streamlit_runtime.session_state[add_key] = ""
                streamlit_runtime.rerun()
            else:
                st.info("All entered tags were already on the allowlist.")

    st.divider()
    st.markdown("#### Rename tag")
    st.caption("Updates this YAML file only; does not rewrite review artifacts or wiki notes.")
    if not tags:
        st.caption("Add tags before renaming.")
    else:
        rename_old_key = f"tag_registry_rename_old_{taxonomy_id}"
        rename_new_key = f"tag_registry_rename_new_{taxonomy_id}"
        if rename_old_key not in streamlit_runtime.session_state:
            streamlit_runtime.session_state[rename_old_key] = tags[0]
        if rename_new_key not in streamlit_runtime.session_state:
            streamlit_runtime.session_state[rename_new_key] = ""
        st.selectbox("Current slug", options=tags, key=rename_old_key)
        st.text_input("New slug", key=rename_new_key, placeholder="new-kebab-slug")
        if st.button("Rename", key=f"tag_registry_rename_btn_{taxonomy_id}"):
            old_slug = str(streamlit_runtime.session_state.get(rename_old_key, ""))
            new_slug = str(streamlit_runtime.session_state.get(rename_new_key, "")).strip()
            try:
                rename_tag_in_list(path, old_slug, new_slug)
            except ValueError as exc:
                st.error(str(exc))
            else:
                st.success(f"Renamed `{old_slug}` → `{normalize_display(new_slug)}`.")
                streamlit_runtime.rerun()

    st.divider()
    st.markdown("#### Remove tags")
    if not tags:
        st.caption("Nothing to remove.")
    else:
        remove_key = f"tag_registry_remove_{taxonomy_id}"
        st.multiselect(
            "Tags to remove",
            options=tags,
            key=remove_key,
            help="Removed slugs stay in existing review JSON until you edit those proposals.",
        )
        confirm_key = f"tag_registry_remove_confirm_{taxonomy_id}"
        confirmed = st.checkbox(
            "I understand this only edits the allowlist YAML",
            key=confirm_key,
        )
        if st.button("Remove selected", key=f"tag_registry_remove_btn_{taxonomy_id}"):
            selected = streamlit_runtime.session_state.get(remove_key) or []
            if not isinstance(selected, list) or not selected:
                st.warning("Select at least one tag to remove.")
            elif not confirmed:
                st.warning("Confirm allowlist-only removal first.")
            else:
                removed = remove_tags_from_list(path, selected)
                if removed:
                    st.success("Removed: " + ", ".join(f"`{t}`" for t in removed))
                    streamlit_runtime.rerun()
                else:
                    st.info("No matching tags were removed.")

    with st.expander("Reset to baseline seeds", expanded=False):
        st.caption(
            f"Overwrite `{rel_path}` with default starter tags "
            f"({len(spec.baseline_tags)} slug(s)). This cannot be undone from the UI."
        )
        reset_confirm_key = f"tag_registry_reset_confirm_{taxonomy_id}"
        reset_typed_key = f"tag_registry_reset_typed_{taxonomy_id}"
        st.checkbox(
            f"I want to reset **{spec.label}** to baseline",
            key=reset_confirm_key,
        )
        st.text_input(
            f'Type "{taxonomy_id}" to confirm',
            key=reset_typed_key,
        )
        if st.button("Reset allowlist to baseline", key=f"tag_registry_reset_btn_{taxonomy_id}"):
            if not streamlit_runtime.session_state.get(reset_confirm_key):
                st.warning("Check the confirmation box first.")
            elif (
                str(streamlit_runtime.session_state.get(reset_typed_key, "")).strip() != taxonomy_id
            ):
                st.warning(f'Type "{taxonomy_id}" exactly to confirm.')
            else:
                write_tag_taxonomy_file(
                    path,
                    list(spec.baseline_tags),
                    comment=spec.description,
                )
                st.success(f"Reset `{rel_path}` to baseline.")
                streamlit_runtime.rerun()


def normalize_display(raw: str) -> str:
    """Normalize slug for success messages (importable without Streamlit)."""
    from src.ingest_review.tags import normalize_tag

    return normalize_tag(raw) or raw.strip()
