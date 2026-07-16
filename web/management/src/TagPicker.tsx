import { useMemo, useState } from "react";
import type { ReactElement } from "react";

import type { ReviewTagChoice } from "./types";

export function normalizeTagSlug(raw: string): string | null {
  const trimmed = raw.trim();
  if (!trimmed || trimmed.includes(",")) {
    return null;
  }
  return trimmed
    .toLowerCase()
    .replace(/_/g, "-")
    .replace(/[^a-z0-9-]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function sortTagOptions(options: ReviewTagChoice[], query: string): ReviewTagChoice[] {
  const normalizedQuery = query.trim().toLowerCase();
  if (!normalizedQuery) {
    return [...options].sort(
      (left, right) => right.usage_count - left.usage_count || left.name.localeCompare(right.name)
    );
  }
  return [...options]
    .map((option) => {
      if (option.name === normalizedQuery) {
        return { option, rank: 0 };
      }
      if (option.name.startsWith(normalizedQuery)) {
        return { option, rank: 1 };
      }
      return { option, rank: 2 };
    })
    .sort(
      (left, right) =>
        left.rank - right.rank ||
        right.option.usage_count - left.option.usage_count ||
        left.option.name.localeCompare(right.option.name)
    )
    .map((entry) => entry.option);
}

export interface TagPickerProps {
  availableTags: ReviewTagChoice[];
  disabled?: boolean;
  loading?: boolean;
  newTags: string[];
  onChange: (tags: string[], newTags: string[]) => void;
  tags: string[];
}

export function TagPicker({
  availableTags,
  disabled = false,
  loading = false,
  newTags,
  onChange,
  tags
}: TagPickerProps): ReactElement {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const normalizedQuery = normalizeTagSlug(query) ?? "";
  const filteredOptions = useMemo(
    () =>
      sortTagOptions(
        availableTags.filter((option) => !tags.includes(option.name)),
        query
      ).slice(0, 12),
    [availableTags, query, tags]
  );
  const canCreate =
    normalizedQuery.length > 0 &&
    !tags.includes(normalizedQuery) &&
    !availableTags.some((option) => option.name === normalizedQuery);

  function addTag(tag: string): void {
    if (disabled || tags.includes(tag)) {
      return;
    }
    const nextTags = [...tags, tag];
    const isNew = !availableTags.some((option) => option.name === tag);
    const nextNewTags = isNew ? [...newTags, tag] : newTags;
    onChange(nextTags, nextNewTags);
    setQuery("");
    setOpen(false);
  }

  function removeTag(tag: string): void {
    if (disabled) {
      return;
    }
    onChange(
      tags.filter((entry) => entry !== tag),
      newTags.filter((entry) => entry !== tag)
    );
  }

  return (
    <label className="tag-picker">
      Entity tags
      <div className="tag-picker-chips">
        {tags.length === 0 ? <span className="tag-picker-empty">No tags selected</span> : null}
        {tags.map((tag) => (
          <span
            className={newTags.includes(tag) ? "tag-chip tag-chip-new" : "tag-chip"}
            key={tag}
          >
            {tag}
            <button
              aria-label={`Remove ${tag}`}
              disabled={disabled}
              onClick={() => removeTag(tag)}
              type="button"
            >
              ×
            </button>
          </span>
        ))}
      </div>
      <input
        aria-expanded={open}
        aria-label="Search or create tags"
        disabled={disabled}
        onBlur={() => {
          window.setTimeout(() => setOpen(false), 120);
        }}
        onChange={(event) => {
          setQuery(event.target.value);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
        placeholder={loading ? "Loading tags..." : "Search tags"}
        role="combobox"
        value={query}
      />
      {open && (filteredOptions.length > 0 || canCreate) ? (
        <ul className="tag-picker-options" role="listbox">
          {filteredOptions.map((option) => (
            <li key={option.name}>
              <button disabled={disabled} onMouseDown={() => addTag(option.name)} type="button">
                {option.name}
              </button>
            </li>
          ))}
          {canCreate ? (
            <li>
              <button
                className="tag-picker-create"
                disabled={disabled}
                onMouseDown={() => addTag(normalizedQuery)}
                type="button"
              >
                Create new tag: {normalizedQuery}
              </button>
            </li>
          ) : null}
        </ul>
      ) : null}
    </label>
  );
}
