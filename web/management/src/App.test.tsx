import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";

const queuePayload = {
  counts: {
    total: 1,
    pending: 0,
    in_progress: 1,
    finished: 0,
    incomplete: 0
  },
  items: [
    {
      source_id: "api-source",
      title: "API Article",
      author: "Ada",
      publication: "Example Weekly",
      published_date: "2026-07-01",
      category: "article",
      status: "in_progress",
      stale: null,
      tags: ["api"],
      entity_counts: { topics: 1, glossary: 1, trends: 1 },
      review_json_path: "/tmp/reviews/api-source/review.json",
      raw_md_available: true
    }
  ],
  limit: 50,
  offset: 0
};

const finishedQueuePayload = {
  counts: {
    total: 2,
    pending: 0,
    in_progress: 1,
    finished: 1,
    incomplete: 0
  },
  items: [
    {
      source_id: "finished-source",
      title: "Finished Article",
      author: "Grace",
      publication: "Example Weekly",
      published_date: "2026-07-02",
      category: "article",
      status: "finished",
      stale: null,
      tags: ["finished"],
      entity_counts: { topics: 0, glossary: 0, trends: 0 },
      review_json_path: "/tmp/reviews/finished-source/review.json",
      raw_md_available: false
    }
  ],
  limit: 50,
  offset: 0
};

const sourcePayload = {
  source_id: "api-source",
  status: "in_progress",
  stale: null,
  metadata: {
    title: "API Article",
    author: "Ada",
    publication: "Example Weekly",
    published_date: "2026-07-01",
    canonical_url: "https://example.test",
    category: "article",
    readwise_id: "rw-api"
  },
  paths: {
    raw_html: "/tmp/raw/api-source.html",
    raw_md: "/tmp/raw/api-source.md",
    review_json: "/tmp/reviews/api-source/review.json"
  },
  summary: {
    short: "API summary",
    key_insights: ["API insight"]
  },
  tags: ["api"],
  entities: {
    topics: [
      {
        title: "API Topic",
        description: "Topic description",
        tags: ["api"],
        evidence: "Evidence",
        raw: {}
      }
    ],
    glossary: [
      {
        title: "API Term",
        description: "Term definition",
        tags: [],
        evidence: "",
        raw: {}
      }
    ],
    trends: [
      {
        title: "API Trend",
        description: "Trend description",
        tags: [],
        evidence: "",
        raw: {}
      }
    ]
  },
  debug: {
    artifact: { llm_output: { source_summary: { summary: "API summary" } } }
  }
};

const finishedSourcePayload = {
  ...sourcePayload,
  source_id: "finished-source",
  status: "finished",
  metadata: {
    ...sourcePayload.metadata,
    title: "Finished Article",
    author: "Grace",
    readwise_id: "rw-finished"
  },
  summary: {
    short: "Finished summary",
    key_insights: []
  },
  tags: ["finished"],
  entities: {
    topics: [],
    glossary: [],
    trends: []
  }
};

const rawPayload = {
  source_id: "api-source",
  available: true,
  content: "Raw article text",
  path: "/tmp/raw/api-source.md"
};

describe("App", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/api/config")) {
          return Response.json({
            mode: "readonly",
            paths: { raw_dir: "/tmp/raw", reviews_dir: "/tmp/reviews" }
          });
        }
        if (url.includes("/api/review/queue") && url.includes("status=finished")) {
          return Response.json(finishedQueuePayload);
        }
        if (url.includes("/api/review/queue")) {
          return Response.json(queuePayload);
        }
        if (url.includes("/api/review/source/finished-source")) {
          return Response.json(finishedSourcePayload);
        }
        if (url.includes("/api/review/source/api-source/raw")) {
          return Response.json(rawPayload);
        }
        if (url.includes("/api/review/source/api-source")) {
          return Response.json(sourcePayload);
        }
        return new Response("not found", { status: 404 });
      })
    );
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("renders the read-only review workspace and on-demand drawers", async () => {
    render(<App />);

    expect(await screen.findByText("Management Web")).toBeInTheDocument();
    expect(screen.getByText("Read-only")).toBeInTheDocument();
    expect(await screen.findByText("API Article")).toBeInTheDocument();
    expect(await screen.findByText("API summary")).toBeInTheDocument();
    expect(await screen.findByText("API Topic")).toBeInTheDocument();
    expect(await screen.findByText("API Term")).toBeInTheDocument();
    expect(await screen.findByText("API Trend")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Approve article" })).toBeDisabled();

    await userEvent.click(screen.getByRole("button", { name: "Show raw source" }));
    expect(await screen.findByText("Raw article text")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Show debug JSON" }));
    await waitFor(() => {
      expect(screen.getByText(/source_summary/)).toBeInTheDocument();
    });
  });

  it("replaces the selected source when filters remove the current selection", async () => {
    render(<App />);

    expect(await screen.findByText("API summary")).toBeInTheDocument();

    await userEvent.selectOptions(screen.getByLabelText("Status"), "finished");

    expect(await screen.findByRole("heading", { name: "Finished Article" })).toBeInTheDocument();
    expect(await screen.findByText("Finished summary")).toBeInTheDocument();
    expect(screen.queryByText("API summary")).not.toBeInTheDocument();
  });
});
