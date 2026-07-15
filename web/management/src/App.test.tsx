import { cleanup, render, screen, waitFor, within } from "@testing-library/react";
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
  decision_counts: {
    not_reviewed: 2,
    approved: 0,
    needs_attention: 0,
    skipped: 0,
    reanalyze_requested: 0
  },
  items: [
    {
      source_id: "newer-source",
      title: "Newer Article",
      author: "Ada",
      publication: "Example Weekly",
      published_date: "2026-07-01",
      category: "article",
      status: "in_progress",
      stale: null,
      tags: ["api"],
      entity_counts: { topics: 1, glossary: 0, trends: 0 },
      review_json_path: "/tmp/reviews/newer-source/review.json",
      raw_md_available: true,
      management_status: null
    },
    {
      source_id: "api-source",
      title: "API Article",
      author: "Ada",
      publication: "Example Weekly",
      published_date: "2026-05-01",
      category: "article",
      status: "in_progress",
      stale: null,
      tags: ["api"],
      entity_counts: { topics: 1, glossary: 1, trends: 1 },
      review_json_path: "/tmp/reviews/api-source/review.json",
      raw_md_available: true,
      management_status: null
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
  decision_counts: {
    not_reviewed: 0,
    approved: 1,
    needs_attention: 0,
    skipped: 0,
    reanalyze_requested: 0
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
      raw_md_available: false,
      management_status: "approved"
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
  management_review: null,
  debug: {
    artifact: { llm_output: { source_summary: { summary: "API summary" } } }
  }
};

const newerSourcePayload = {
  ...sourcePayload,
  source_id: "newer-source",
  metadata: {
    ...sourcePayload.metadata,
    title: "Newer Article",
    published_date: "2026-07-01"
  },
  summary: {
    short: "Newer summary",
    key_insights: []
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

const approvedSourcePayload = {
  ...sourcePayload,
  management_review: {
    status: "approved",
    reviewed_at: "2026-07-15T12:34:56Z",
    reviewed_by: "plischke",
    notes: "Looks good."
  }
};

const decisionResponse = {
  source_id: "api-source",
  management_review: approvedSourcePayload.management_review,
  backup_path: "/tmp/reviews/api-source/review.before-management-review.20260715T123456Z.json"
};

const approvedQueuePayload = {
  ...queuePayload,
  decision_counts: {
    not_reviewed: 2,
    approved: 1,
    needs_attention: 0,
    skipped: 0,
    reanalyze_requested: 0
  },
  items: [{ ...queuePayload.items[1], management_status: "approved" }]
};

const onlyNewerQueuePayload = {
  ...queuePayload,
  decision_counts: {
    not_reviewed: 1,
    approved: 1,
    needs_attention: 0,
    skipped: 0,
    reanalyze_requested: 0
  },
  items: [queuePayload.items[0]]
};

const emptyQueuePayload = {
  ...queuePayload,
  decision_counts: {
    not_reviewed: 0,
    approved: 1,
    needs_attention: 0,
    skipped: 0,
    reanalyze_requested: 0
  },
  items: []
};

describe("App", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input);
        if (url.includes("/api/config")) {
          return Response.json({
            mode: "readonly",
            paths: { raw_dir: "/tmp/raw", reviews_dir: "/tmp/reviews" }
          });
        }
        if (url.includes("/api/review/source/api-source/decision") && init?.method === "PATCH") {
          return Response.json(decisionResponse);
        }
        if (url.includes("/api/review/queue") && url.includes("decision=approved")) {
          return Response.json(approvedQueuePayload);
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
        if (url.includes("/api/review/source/newer-source")) {
          return Response.json(newerSourcePayload);
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

    expect(await screen.findByText("Review Workspace")).toBeInTheDocument();
    expect(screen.getByText("Write enabled")).toBeInTheDocument();
    expect(await screen.findByRole("heading", { name: "API Article" })).toBeInTheDocument();
    expect(screen.getAllByText("Ready for review").length).toBeGreaterThan(0);
    expect(await screen.findByText("API summary")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Easy Read" })).toBeInTheDocument();
    expect(await screen.findByText("API Topic")).toBeInTheDocument();
    expect(await screen.findByText("API Term")).toBeInTheDocument();
    expect(await screen.findByText("API Trend")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Previous" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Next" })).not.toBeDisabled();
    expect(screen.getByRole("button", { name: "Approve article" })).toBeEnabled();

    await userEvent.click(screen.getByRole("button", { name: "Show raw source" }));
    expect(await screen.findByText("Raw article text")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Show debug JSON" }));
    await waitFor(() => {
      expect(screen.getByText(/source_summary/)).toBeInTheDocument();
    });

    expect(
      vi
        .mocked(fetch)
        .mock.calls.some(
          ([input]) =>
            String(input).includes("status=in_progress") &&
            String(input).includes("decision=not_reviewed")
        )
    ).toBe(true);
  });

  it("sorts visible queue rows by oldest published date first", async () => {
    render(<App />);

    const sourceList = await screen.findByLabelText("Source list");
    const rows = within(sourceList).getAllByRole("button");

    expect(rows[0]).toHaveTextContent("API Article");
    expect(rows[1]).toHaveTextContent("Newer Article");
  });

  it("renders current management decision state when present", async () => {
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/config")) {
        return Response.json({
          mode: "readonly",
          paths: { raw_dir: "/tmp/raw", reviews_dir: "/tmp/reviews" }
        });
      }
      if (url.includes("/api/review/queue")) {
        return Response.json({
          ...queuePayload,
          items: [{ ...queuePayload.items[1], management_status: "approved" }]
        });
      }
      if (url.includes("/api/review/source/api-source")) {
        return Response.json(approvedSourcePayload);
      }
      return new Response("not found", { status: 404 });
    });

    render(<App />);

    expect(await screen.findByText("Decision: Approved")).toBeInTheDocument();
    expect(screen.getByText("Reviewed by plischke")).toBeInTheDocument();
    expect(screen.getByText("Looks good.")).toBeInTheDocument();
    expect(within(await screen.findByLabelText("Source list")).getByText("Approved")).toBeInTheDocument();
  });

  it("switches the decision filter to show decided articles with badges", async () => {
    render(<App />);

    await screen.findByText("API summary");
    await userEvent.selectOptions(screen.getByLabelText("Decision"), "approved");

    expect(within(await screen.findByLabelText("Source list")).getByText("Approved")).toBeInTheDocument();
    expect(await screen.findByRole("heading", { name: "API Article" })).toBeInTheDocument();
    expect(
      vi
        .mocked(fetch)
        .mock.calls.some(([input]) => String(input).includes("decision=approved"))
    ).toBe(true);
  });

  it("writes approve decisions and reloads source and queue state", async () => {
    render(<App />);

    await screen.findByText("API summary");
    await userEvent.click(screen.getByRole("button", { name: "Approve article" }));

    await waitFor(() => {
      expect(vi.mocked(fetch)).toHaveBeenCalledWith(
        "/api/review/source/api-source/decision",
        expect.objectContaining({
          body: JSON.stringify({ status: "approved", notes: "" }),
          method: "PATCH"
        })
      );
    });
    await waitFor(() => {
      const queueCalls = vi
        .mocked(fetch)
        .mock.calls.filter(([input]) => String(input).includes("/api/review/queue"));
      const sourceCalls = vi
        .mocked(fetch)
        .mock.calls.filter(([input]) => String(input).includes("/api/review/source/api-source"));
      expect(queueCalls.length).toBeGreaterThanOrEqual(2);
      expect(sourceCalls.length).toBeGreaterThanOrEqual(2);
    });
    expect(await screen.findByText("Decision saved: approved")).toBeInTheDocument();
  });

  it("selects the next undecided source after approving the current source", async () => {
    let queueCalls = 0;
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/api/config")) {
        return Response.json({
          mode: "readonly",
          paths: { raw_dir: "/tmp/raw", reviews_dir: "/tmp/reviews" }
        });
      }
      if (url.includes("/api/review/source/api-source/decision") && init?.method === "PATCH") {
        return Response.json(decisionResponse);
      }
      if (url.includes("/api/review/queue")) {
        queueCalls += 1;
        return Response.json(queueCalls > 1 ? onlyNewerQueuePayload : queuePayload);
      }
      if (url.includes("/api/review/source/newer-source")) {
        return Response.json(newerSourcePayload);
      }
      if (url.includes("/api/review/source/api-source")) {
        return Response.json(sourcePayload);
      }
      return new Response("not found", { status: 404 });
    });

    render(<App />);

    expect(await screen.findByText("API summary")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Approve article" }));

    expect(await screen.findByRole("heading", { name: "Newer Article" })).toBeInTheDocument();
    expect(await screen.findByText("Newer summary")).toBeInTheDocument();
    expect(screen.queryByText("Decision saved: approved")).not.toBeInTheDocument();
  });

  it("clears the selected source after approving the last undecided source", async () => {
    let queueCalls = 0;
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/api/config")) {
        return Response.json({
          mode: "readonly",
          paths: { raw_dir: "/tmp/raw", reviews_dir: "/tmp/reviews" }
        });
      }
      if (url.includes("/api/review/source/api-source/decision") && init?.method === "PATCH") {
        return Response.json(decisionResponse);
      }
      if (url.includes("/api/review/queue")) {
        queueCalls += 1;
        return Response.json(queueCalls > 1 ? emptyQueuePayload : {
          ...queuePayload,
          items: [queuePayload.items[1]]
        });
      }
      if (url.includes("/api/review/source/api-source")) {
        return Response.json(sourcePayload);
      }
      return new Response("not found", { status: 404 });
    });

    render(<App />);

    expect(await screen.findByText("API summary")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Approve article" }));

    expect(await screen.findByText("No sources match.")).toBeInTheDocument();
    expect(screen.getByText("Select a source to inspect its review artifact.")).toBeInTheDocument();
    expect(screen.queryByText("Decision saved: approved")).not.toBeInTheDocument();
  });

  it("disables article action buttons while a decision request is pending", async () => {
    let resolveDecision: (response: Response) => void = () => undefined;
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/api/config")) {
        return Response.json({
          mode: "readonly",
          paths: { raw_dir: "/tmp/raw", reviews_dir: "/tmp/reviews" }
        });
      }
      if (url.includes("/api/review/queue")) {
        return Response.json(queuePayload);
      }
      if (url.includes("/api/review/source/api-source/decision") && init?.method === "PATCH") {
        return await new Promise<Response>((resolve) => {
          resolveDecision = resolve;
        });
      }
      if (url.includes("/api/review/source/api-source")) {
        return Response.json(sourcePayload);
      }
      return new Response("not found", { status: 404 });
    });
    render(<App />);

    await screen.findByText("API summary");
    await userEvent.click(screen.getByRole("button", { name: "Approve article" }));

    expect(screen.getByRole("button", { name: "Approve article" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Needs attention" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Skip" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Request re-analysis" })).toBeDisabled();

    resolveDecision(Response.json(decisionResponse));
  });

  it("shows decision write errors", async () => {
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/api/config")) {
        return Response.json({
          mode: "readonly",
          paths: { raw_dir: "/tmp/raw", reviews_dir: "/tmp/reviews" }
        });
      }
      if (url.includes("/api/review/queue")) {
        return Response.json(queuePayload);
      }
      if (url.includes("/api/review/source/api-source/decision") && init?.method === "PATCH") {
        return new Response("failed", { status: 500, statusText: "Server Error" });
      }
      if (url.includes("/api/review/source/api-source")) {
        return Response.json(sourcePayload);
      }
      return new Response("not found", { status: 404 });
    });
    render(<App />);

    await screen.findByText("API summary");
    await userEvent.click(screen.getByRole("button", { name: "Approve article" }));

    expect(await screen.findByText(/Decision failed/)).toBeInTheDocument();
  });

  it("keeps saved decision feedback when refresh after a successful write fails", async () => {
    let queueCalls = 0;
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/api/config")) {
        return Response.json({
          mode: "readonly",
          paths: { raw_dir: "/tmp/raw", reviews_dir: "/tmp/reviews" }
        });
      }
      if (url.includes("/api/review/source/api-source/decision") && init?.method === "PATCH") {
        return Response.json(decisionResponse);
      }
      if (url.includes("/api/review/queue")) {
        queueCalls += 1;
        if (queueCalls > 1) {
          return new Response("failed", { status: 500, statusText: "Server Error" });
        }
        return Response.json(queuePayload);
      }
      if (url.includes("/api/review/source/api-source")) {
        return Response.json(sourcePayload);
      }
      return new Response("not found", { status: 404 });
    });
    render(<App />);

    await screen.findByText("API summary");
    await userEvent.click(screen.getByRole("button", { name: "Approve article" }));

    expect(await screen.findByText("Decision saved: approved")).toBeInTheDocument();
    expect(await screen.findByText(/Refresh failed/)).toBeInTheDocument();
    expect(screen.queryByText(/Decision failed/)).not.toBeInTheDocument();
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
