import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { TagPicker } from "./TagPicker";
import type { ReviewTagChoice } from "./types";

function makeTags(count: number): ReviewTagChoice[] {
  return Array.from({ length: count }, (_, index) => ({
    name: `tag-${String(index + 1).padStart(2, "0")}`,
    source: "registry" as const,
    usage_count: count - index
  }));
}

describe("TagPicker", () => {
  it("shows the full allowlist without truncating to twelve options", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(
      <TagPicker
        availableTags={makeTags(20)}
        newTags={[]}
        onChange={onChange}
        tags={[]}
      />
    );

    await user.click(screen.getByLabelText("Search or create tags"));

    expect(screen.getByRole("button", { name: "tag-01" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "tag-20" })).toBeInTheDocument();
    expect(screen.getAllByRole("button").filter((button) => button.textContent?.startsWith("tag-"))).toHaveLength(
      20
    );
  });

  it("renders a custom label and helper text", () => {
    render(
      <TagPicker
        availableTags={[]}
        helperText="What kind of product?"
        label="Tool kind"
        newTags={[]}
        onChange={vi.fn()}
        tags={[]}
      />
    );

    expect(screen.getByText("Tool kind")).toBeInTheDocument();
    expect(screen.getByText("What kind of product?")).toBeInTheDocument();
  });
});
