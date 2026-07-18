import { cleanup, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";

function makeEntity(
  index: number,
  title: string,
  options: {
    description?: string;
    tags?: string[];
    hidden?: boolean;
    detail_scalars?: Array<{ label: string; body: string }>;
    detail_lists?: Array<{ label: string; items: string[] }>;
    render_category?: string;
    render_mode?: "merged" | "individual";
    section?: "wiki_entities" | "source_specific_insights";
  } = {}
) {
  return {
    index,
    title,
    description: options.description ?? "",
    tags: options.tags ?? [],
    types: [],
    evidence: "",
    hidden: options.hidden ?? false,
    render_category: options.render_category ?? "topic",
    render_mode: options.render_mode ?? "merged",
    detail_scalars: options.detail_scalars ?? [],
    detail_lists: options.detail_lists ?? [],
    raw: {}
  };
}

function buildEntityGroups(
  entries: Array<{
    group:
      | "topics"
      | "glossary"
      | "trends"
      | "how_to"
      | "tools"
      | "models"
      | "implementation_studies"
      | "signals"
      | "interview_insights";
    label: string;
    section: "wiki_entities" | "source_specific_insights";
    items: ReturnType<typeof makeEntity>[];
  }>
) {
  const byGroup = Object.fromEntries(entries.map((entry) => [entry.group, entry.items]));
  return {
    topics: byGroup.topics ?? [],
    glossary: byGroup.glossary ?? [],
    trends: byGroup.trends ?? [],
    groups: entries
  };
}

const emptyEntityCounts = {
  topics: 0,
  glossary: 0,
  trends: 0,
  how_to: 0,
  tools: 0,
  models: 0,
  implementation_studies: 0,
  signals: 0,
  interview_insights: 0
};

const configPayload = {
  mode: "write_enabled",
  capabilities: ["review_decision", "review_entity_edit", "review_finish"],
  paths: {
    repo_root: "/tmp/repo",
    knowledge_root: "/tmp/knowledge",
    vault_root: "/tmp/vault",
    raw_dir: "/tmp/raw",
    reviews_dir: "/tmp/reviews",
    wiki_dir: "/tmp/wiki"
  }
};

const tagRegistryPayload = {
  tags: [
    { name: "api", source: "registry", usage_count: 5 },
    { name: "agent-systems", source: "registry", usage_count: 42 }
  ]
};

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
      entity_counts: { ...emptyEntityCounts, topics: 1 },
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
      entity_counts: { ...emptyEntityCounts, topics: 1, glossary: 1, trends: 1 },
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
      entity_counts: emptyEntityCounts,
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
    key_insights: ["API insight"],
    chapters: []
  },
  tags: ["api"],
  entities: buildEntityGroups([
    {
      group: "topics",
      label: "Topics",
      section: "wiki_entities",
      items: [
        makeEntity(0, "API Topic", {
          description: "Topic description",
          tags: ["api"],
          render_category: "topic"
        })
      ]
    },
    {
      group: "glossary",
      label: "Glossary",
      section: "wiki_entities",
      items: [
        makeEntity(0, "API Term", {
          description: "Term definition",
          render_category: "glossary"
        })
      ]
    },
    {
      group: "trends",
      label: "Trends",
      section: "wiki_entities",
      items: [
        makeEntity(0, "API Trend", {
          description: "Trend description",
          render_category: "trend"
        })
      ]
    }
  ]),
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
    key_insights: [],
    chapters: []
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
    key_insights: [],
    chapters: []
  },
  tags: ["finished"],
  entities: buildEntityGroups([]),
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

const needsAttentionDecisionResponse = {
  source_id: "api-source",
  management_review: {
    status: "needs_attention",
    reviewed_at: "2026-07-15T12:34:56Z",
    reviewed_by: "plischke",
    notes: ""
  },
  backup_path: "/tmp/reviews/api-source/review.before-management-review.20260715T123456Z.json"
};

const finishResponse = {
  source_id: "api-source",
  management_review: approvedSourcePayload.management_review,
  review_finished_at: "2026-07-15T12:34:56Z",
  backup_path: "/tmp/reviews/api-source/review.before-management-edit.20260715T123456Z.json"
};

const editedSourcePayload = {
  ...sourcePayload,
  tags: ["api", "edited"],
  entities: buildEntityGroups([
    {
      group: "topics",
      label: "Topics",
      section: "wiki_entities",
      items: [
        makeEntity(0, "Edited topic", {
          description: "Edited description.",
          tags: ["api", "edited"],
          render_category: "topic"
        })
      ]
    },
    {
      group: "glossary",
      label: "Glossary",
      section: "wiki_entities",
      items: sourcePayload.entities.glossary
    },
    {
      group: "trends",
      label: "Trends",
      section: "wiki_entities",
      items: sourcePayload.entities.trends
    }
  ])
};

const hiddenSourcePayload = {
  ...sourcePayload,
  entities: buildEntityGroups([
    {
      group: "topics",
      label: "Topics",
      section: "wiki_entities",
      items: [
        makeEntity(0, "API Topic", {
          description: "Topic description",
          tags: ["api"],
          hidden: true,
          render_category: "topic"
        })
      ]
    },
    {
      group: "glossary",
      label: "Glossary",
      section: "wiki_entities",
      items: sourcePayload.entities.glossary
    },
    {
      group: "trends",
      label: "Trends",
      section: "wiki_entities",
      items: sourcePayload.entities.trends
    }
  ])
};

const noDescriptionSourcePayload = {
  ...sourcePayload,
  entities: buildEntityGroups([
    {
      group: "topics",
      label: "Topics",
      section: "wiki_entities",
      items: [
        makeEntity(0, "API Topic", {
          tags: ["api"],
          render_category: "topic"
        })
      ]
    },
    {
      group: "glossary",
      label: "Glossary",
      section: "wiki_entities",
      items: sourcePayload.entities.glossary
    },
    {
      group: "trends",
      label: "Trends",
      section: "wiki_entities",
      items: sourcePayload.entities.trends
    }
  ])
};

const entityEditResponse = {
  source_id: "api-source",
  group: "topics",
  index: 0,
  backup_path: "/tmp/reviews/api-source/review.before-management-edit.20260715T123456Z.json",
  source: editedSourcePayload
};

const hiddenEntityResponse = {
  ...entityEditResponse,
  source: hiddenSourcePayload
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

const pipelineOperationsPayload = {
  operations: [
    {
      id: "wiki_lint",
      label: "Wiki lint",
      description: "Validate generated wiki markdown and vault hygiene without writes.",
      writes: false,
      llm_calls: false,
      requires_confirmation: false,
      parameters: []
    },
    {
      id: "wiki_render_dry_run",
      label: "Wiki render dry-run",
      description: "Preview generated Obsidian wiki pages.",
      writes: false,
      llm_calls: false,
      requires_confirmation: false,
      parameters: [
        {
          name: "require_source_text",
          label: "Require source text",
          type: "boolean",
          default: true
        }
      ]
    },
    {
      id: "wiki_render",
      label: "Wiki render",
      description: "Write generated Obsidian wiki pages.",
      writes: true,
      llm_calls: false,
      requires_confirmation: true,
      parameters: [
        {
          name: "require_source_text",
          label: "Require source text",
          type: "boolean",
          default: true
        }
      ]
    },
    {
      id: "synthesis_select",
      label: "Synthesis select",
      description: "Rank changed synthesis candidates without LLM calls.",
      writes: false,
      llm_calls: false,
      requires_confirmation: false,
      parameters: [
        {
          name: "limit",
          label: "Limit",
          type: "integer",
          default: 20
        }
      ]
    },
    {
      id: "synthesis_batch_dry_run",
      label: "Synthesis batch dry-run",
      description: "Preview a synthesis batch.",
      writes: false,
      llm_calls: false,
      requires_confirmation: false,
      parameters: [
        {
          name: "limit",
          label: "Limit",
          type: "integer",
          default: 5
        }
      ]
    },
    {
      id: "synthesis_batch",
      label: "Synthesis batch",
      description: "Run a bounded synthesis batch.",
      writes: true,
      llm_calls: true,
      requires_confirmation: true,
      parameters: [
        {
          name: "limit",
          label: "Limit",
          type: "integer",
          default: 5
        },
        {
          name: "between_calls",
          label: "Pause between calls",
          type: "integer",
          default: 300
        }
      ]
    }
  ]
};

const pipelineRunsPayload = {
  runs: [
    {
      run_id: "run-failed",
      operation_id: "wiki_lint",
      label: "Wiki lint",
      status: "failed",
      started_at: "2026-07-16T12:57:28Z",
      finished_at: "2026-07-16T12:57:30Z",
      duration_seconds: 2,
      exit_code: 2,
      writes: false,
      llm_calls: false,
      report_path: null,
      stdout_tail: "",
      stderr_tail: "lint failed"
    },
    {
      run_id: "run-ok",
      operation_id: "synthesis_select",
      label: "Synthesis select",
      status: "succeeded",
      started_at: "2026-07-16T12:55:28Z",
      finished_at: "2026-07-16T12:55:30Z",
      duration_seconds: 2,
      exit_code: 0,
      writes: false,
      llm_calls: false,
      report_path: null,
      stdout_tail: "select ok",
      stderr_tail: ""
    }
  ]
};

describe("App", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input);
        if (url.includes("/api/config")) {
          return Response.json(configPayload);
        }
        if (url.includes("/api/review/tags")) {
          return Response.json(tagRegistryPayload);
        }
        if (url.includes("/api/review/source/api-source/decision") && init?.method === "PATCH") {
          return Response.json(decisionResponse);
        }
        if (url.includes("/api/review/source/api-source/entity") && init?.method === "PATCH") {
          return Response.json(entityEditResponse);
        }
        if (url.includes("/api/review/source/api-source/finish") && init?.method === "PATCH") {
          return Response.json(finishResponse);
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
        if (url.includes("/api/ops/workflows/update-wiki/status")) {
          return Response.json({
            update_available: true,
            headline: "Wiki update available",
            detail_line: "1 sources · 0 reviewed · render incomplete",
            hints: [],
            blocking_errors: [],
            can_start: true,
            collected_at: "2026-07-16T10:00:00Z"
          });
        }
        if (url.includes("/api/ops/workflows/update-wiki/active")) {
          return Response.json({ run: null });
        }
        if (url.includes("/api/ops/status")) {
          return Response.json({
            status: { recommendations: ["Run wiki-render --dry-run to refresh the render snapshot."] },
            collected_at: "2026-07-16T10:00:00Z",
            summary: "1 sources · 0 reviewed · render incomplete"
          });
        }
        if (url.includes("/api/ops/operations")) {
          return Response.json(pipelineOperationsPayload);
        }
        if (url.includes("/api/ops/runs")) {
          return Response.json(pipelineRunsPayload);
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
    expect(screen.getAllByText("Ready to review").length).toBeGreaterThan(0);
    expect(screen.getByRole("heading", { name: "Easy Read" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Extraction overview" })).toBeInTheDocument();
    expect(await screen.findByText("API summary")).toBeInTheDocument();
    expect(await screen.findByText("API Topic")).toBeInTheDocument();
    expect(await screen.findByText("API Term")).toBeInTheDocument();
    expect(await screen.findByText("API Trend")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Previous" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Next" })).not.toBeDisabled();
    expect(screen.getByRole("button", { name: "Finish as approved" })).toBeEnabled();
    expect(screen.queryByRole("button", { name: "Approve article" })).not.toBeInTheDocument();

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
          mode: "write_enabled",
            capabilities: ["review_decision", "review_entity_edit", "review_finish"],
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

    expect(await screen.findByRole("heading", { name: "API Article" })).toBeInTheDocument();
    expect(
      within(await screen.findByLabelText("Source list")).getByText("Approved")
    ).toBeInTheDocument();
    await userEvent.click(await screen.findByText("Source details"));
    expect(await screen.findByText("plischke")).toBeInTheDocument();
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

  it("opens one entity editor and cancels without saving", async () => {
    render(<App />);

    await screen.findByText("API summary");
    await userEvent.click(screen.getByRole("button", { name: "Edit API Topic" }));

    expect(screen.getByLabelText("Entity title")).toHaveValue("API Topic");
    expect(screen.getByLabelText("Entity description")).toHaveValue("Topic description");
    expect(screen.getByRole("button", { name: "Remove api" })).toBeInTheDocument();
    expect(screen.getByLabelText("Search or create tags")).toBeInTheDocument();
    expect(screen.queryByLabelText("Hidden")).not.toBeInTheDocument();
    expect(screen.getByText("Change title, description, or tags to save.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Save entity" })).toBeDisabled();

    await userEvent.clear(screen.getByLabelText("Entity title"));
    await userEvent.type(screen.getByLabelText("Entity title"), "Draft title");
    await userEvent.click(screen.getByRole("button", { name: "Cancel edit" }));

    expect(await screen.findByText("API Topic")).toBeInTheDocument();
    expect(screen.queryByDisplayValue("Draft title")).not.toBeInTheDocument();
    expect(
      vi
        .mocked(fetch)
        .mock.calls.some(([input]) => String(input).includes("/api/review/source/api-source/entity"))
    ).toBe(false);
  });

  it("saves entity edits and refreshes the displayed source from the response", async () => {
    render(<App />);

    await screen.findByText("API summary");
    await userEvent.click(screen.getByRole("button", { name: "Edit API Topic" }));
    await userEvent.clear(screen.getByLabelText("Entity title"));
    await userEvent.type(screen.getByLabelText("Entity title"), "Edited topic");
    await userEvent.clear(screen.getByLabelText("Entity description"));
    await userEvent.type(screen.getByLabelText("Entity description"), "Edited description.");
    const tagSearch = await screen.findByLabelText("Search or create tags");
    await userEvent.type(tagSearch, "edited");
    await userEvent.click(await screen.findByRole("button", { name: "Create new tag: edited" }));
    await userEvent.click(screen.getByRole("button", { name: "Save entity" }));

    await waitFor(() => {
      expect(vi.mocked(fetch)).toHaveBeenCalledWith(
        "/api/review/source/api-source/entity",
        expect.objectContaining({
          body: JSON.stringify({
            group: "topics",
            index: 0,
            title: "Edited topic",
            description: "Edited description.",
            tags: ["api", "edited"]
          }),
          method: "PATCH"
        })
      );
    });
    await waitFor(() => {
      const queueCalls = vi
        .mocked(fetch)
        .mock.calls.filter(([input]) => String(input).includes("/api/review/queue"));
      expect(queueCalls.length).toBeGreaterThanOrEqual(2);
    });
    expect(await screen.findByText("Edited topic")).toBeInTheDocument();
    expect(await screen.findByText("Entity saved.")).toBeInTheDocument();
  });

  it("shows inline validation and server errors for entity edits", async () => {
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/api/config")) {
        return Response.json({
          mode: "write_enabled",
            capabilities: ["review_decision", "review_entity_edit", "review_finish"],
          paths: { raw_dir: "/tmp/raw", reviews_dir: "/tmp/reviews" }
        });
      }
      if (url.includes("/api/review/queue")) {
        return Response.json(queuePayload);
      }
      if (url.includes("/api/review/source/api-source/entity") && init?.method === "PATCH") {
        return new Response("failed", { status: 500, statusText: "Server Error" });
      }
      if (url.includes("/api/review/source/api-source")) {
        return Response.json(sourcePayload);
      }
      return new Response("not found", { status: 404 });
    });
    render(<App />);

    await screen.findByText("API summary");
    await userEvent.click(screen.getByRole("button", { name: "Edit API Topic" }));
    await userEvent.clear(screen.getByLabelText("Entity title"));

    expect(screen.getByRole("button", { name: "Save entity" })).toBeDisabled();
    expect(screen.getByText("Title cannot be empty.")).toBeInTheDocument();

    await userEvent.type(screen.getByLabelText("Entity title"), "Valid title");
    await userEvent.click(screen.getByRole("button", { name: "Save entity" }));

    expect(await screen.findByText(/Entity save failed/)).toBeInTheDocument();
  });

  it("rejects entities from the default list and reveals them with show rejected", async () => {
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/api/config")) {
        return Response.json({
          mode: "write_enabled",
            capabilities: ["review_decision", "review_entity_edit", "review_finish"],
          paths: { raw_dir: "/tmp/raw", reviews_dir: "/tmp/reviews" }
        });
      }
      if (url.includes("/api/review/tags")) {
        return Response.json(tagRegistryPayload);
      }
      if (url.includes("/api/review/queue")) {
        return Response.json(queuePayload);
      }
      if (url.includes("/api/review/source/api-source/entity") && init?.method === "PATCH") {
        return Response.json(hiddenEntityResponse);
      }
      if (url.includes("/api/review/source/api-source")) {
        return Response.json(sourcePayload);
      }
      return new Response("not found", { status: 404 });
    });
    render(<App />);

    await screen.findByText("API summary");
    await userEvent.click(screen.getByRole("button", { name: "Reject API Topic" }));

    await waitFor(() => expect(screen.queryByText("API Topic")).not.toBeInTheDocument());
    await userEvent.click(screen.getByLabelText("Show rejected entities (1)"));

    expect(await screen.findByText("API Topic")).toBeInTheDocument();
    expect(screen.getByText("Rejected")).toBeInTheDocument();
  });

  it("omits unchanged empty description fields when rejecting an entity", async () => {
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/api/config")) {
        return Response.json({
          mode: "write_enabled",
            capabilities: ["review_decision", "review_entity_edit", "review_finish"],
          paths: { raw_dir: "/tmp/raw", reviews_dir: "/tmp/reviews" }
        });
      }
      if (url.includes("/api/review/queue")) {
        return Response.json(queuePayload);
      }
      if (url.includes("/api/review/source/api-source/entity") && init?.method === "PATCH") {
        return Response.json(hiddenEntityResponse);
      }
      if (url.includes("/api/review/source/api-source")) {
        return Response.json(noDescriptionSourcePayload);
      }
      return new Response("not found", { status: 404 });
    });
    render(<App />);

    await screen.findByText("API summary");
    await userEvent.click(screen.getByRole("button", { name: "Reject API Topic" }));

    await waitFor(() => {
      expect(vi.mocked(fetch)).toHaveBeenCalledWith(
        "/api/review/source/api-source/entity",
        expect.objectContaining({
          body: JSON.stringify({ group: "topics", index: 0, hidden: true }),
          method: "PATCH"
        })
      );
    });
  });

  it("writes secondary decisions and reloads source and queue state", async () => {
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/api/config")) {
        return Response.json(configPayload);
      }
      if (url.includes("/api/review/tags")) {
        return Response.json(tagRegistryPayload);
      }
      if (url.includes("/api/review/source/api-source/decision") && init?.method === "PATCH") {
        return Response.json(needsAttentionDecisionResponse);
      }
      if (url.includes("/api/review/queue")) {
        return Response.json(queuePayload);
      }
      if (url.includes("/api/review/source/api-source")) {
        return Response.json(sourcePayload);
      }
      return new Response("not found", { status: 404 });
    });
    render(<App />);

    await screen.findByText("API summary");
    await userEvent.click(screen.getByRole("button", { name: "Needs attention" }));

    await waitFor(() => {
      expect(vi.mocked(fetch)).toHaveBeenCalledWith(
        "/api/review/source/api-source/decision",
        expect.objectContaining({
          body: JSON.stringify({ status: "needs_attention", notes: "" }),
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
    expect(await screen.findByText("Decision saved: needs_attention")).toBeInTheDocument();
  });

  it("selects the next undecided source after finishing the current source", async () => {
    let queueCalls = 0;
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/api/config")) {
        return Response.json({
          mode: "write_enabled",
            capabilities: ["review_decision", "review_entity_edit", "review_finish"],
          paths: { raw_dir: "/tmp/raw", reviews_dir: "/tmp/reviews" }
        });
      }
      if (url.includes("/api/review/source/api-source/finish") && init?.method === "PATCH") {
        return Response.json(finishResponse);
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
    await userEvent.click(screen.getByRole("button", { name: "Finish as approved" }));

    expect(await screen.findByRole("heading", { name: "Newer Article" })).toBeInTheDocument();
    expect(await screen.findByText("Newer summary")).toBeInTheDocument();
  });

  it("clears the selected source after finishing the last undecided source", async () => {
    let queueCalls = 0;
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/api/config")) {
        return Response.json({
          mode: "write_enabled",
            capabilities: ["review_decision", "review_entity_edit", "review_finish"],
          paths: { raw_dir: "/tmp/raw", reviews_dir: "/tmp/reviews" }
        });
      }
      if (url.includes("/api/review/source/api-source/finish") && init?.method === "PATCH") {
        return Response.json(finishResponse);
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
    await userEvent.click(screen.getByRole("button", { name: "Finish as approved" }));

    expect(await screen.findByText("No sources match.")).toBeInTheDocument();
    expect(screen.getByText("Select a source to inspect its review artifact.")).toBeInTheDocument();
  });

  it("disables article action buttons while a decision request is pending", async () => {
    let resolveDecision: (response: Response) => void = () => undefined;
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/api/config")) {
        return Response.json({
          mode: "write_enabled",
            capabilities: ["review_decision", "review_entity_edit", "review_finish"],
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
    await userEvent.click(screen.getByRole("button", { name: "Needs attention" }));

    expect(screen.getByRole("button", { name: "Finish as approved" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Needs attention" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Skip" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Request re-analysis" })).toBeDisabled();

    resolveDecision(Response.json(needsAttentionDecisionResponse));
  });

  it("shows decision write errors", async () => {
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/api/config")) {
        return Response.json({
          mode: "write_enabled",
            capabilities: ["review_decision", "review_entity_edit", "review_finish"],
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
    await userEvent.click(screen.getByRole("button", { name: "Needs attention" }));

    expect(await screen.findByText(/Decision failed/)).toBeInTheDocument();
  });

  it("keeps saved decision feedback when refresh after a successful write fails", async () => {
    let queueCalls = 0;
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/api/config")) {
        return Response.json({
          mode: "write_enabled",
            capabilities: ["review_decision", "review_entity_edit", "review_finish"],
          paths: { raw_dir: "/tmp/raw", reviews_dir: "/tmp/reviews" }
        });
      }
      if (url.includes("/api/review/source/api-source/decision") && init?.method === "PATCH") {
        return Response.json(needsAttentionDecisionResponse);
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
    await userEvent.click(screen.getByRole("button", { name: "Needs attention" }));

    expect(await screen.findByText("Decision saved: needs_attention")).toBeInTheDocument();
    expect(await screen.findByText(/Refresh failed/)).toBeInTheDocument();
    expect(screen.queryByText(/Decision failed/)).not.toBeInTheDocument();
  });

  it("finishes the current review and selects the next matching source", async () => {
    let queueCalls = 0;
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/api/config")) {
        return Response.json({
          mode: "write_enabled",
            capabilities: ["review_decision", "review_entity_edit", "review_finish"],
          paths: { raw_dir: "/tmp/raw", reviews_dir: "/tmp/reviews" }
        });
      }
      if (url.includes("/api/review/source/api-source/finish") && init?.method === "PATCH") {
        return Response.json(finishResponse);
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

    await screen.findByText("API summary");
    await userEvent.click(screen.getByRole("button", { name: "Finish as approved" }));

    await waitFor(() => {
      expect(vi.mocked(fetch)).toHaveBeenCalledWith(
        "/api/review/source/api-source/finish",
        expect.objectContaining({
          body: JSON.stringify({ notes: "", force: false }),
          method: "PATCH"
        })
      );
    });
    expect(await screen.findByRole("heading", { name: "Newer Article" })).toBeInTheDocument();
    expect(await screen.findByText("Newer summary")).toBeInTheDocument();
  });

  it("shows the empty state after finishing the last matching source", async () => {
    let queueCalls = 0;
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/api/config")) {
        return Response.json({
          mode: "write_enabled",
            capabilities: ["review_decision", "review_entity_edit", "review_finish"],
          paths: { raw_dir: "/tmp/raw", reviews_dir: "/tmp/reviews" }
        });
      }
      if (url.includes("/api/review/source/api-source/finish") && init?.method === "PATCH") {
        return Response.json(finishResponse);
      }
      if (url.includes("/api/review/queue")) {
        queueCalls += 1;
        return Response.json(queueCalls > 1 ? emptyQueuePayload : { ...queuePayload, items: [queuePayload.items[1]] });
      }
      if (url.includes("/api/review/source/api-source")) {
        return Response.json(sourcePayload);
      }
      return new Response("not found", { status: 404 });
    });
    render(<App />);

    await screen.findByText("API summary");
    await userEvent.click(screen.getByRole("button", { name: "Finish as approved" }));

    expect(await screen.findByText("No sources match.")).toBeInTheDocument();
    expect(screen.getByText("Select a source to inspect its review artifact.")).toBeInTheDocument();
  });

  it("shows finish conflicts and keeps the current source visible", async () => {
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/api/config")) {
        return Response.json({
          mode: "write_enabled",
            capabilities: ["review_decision", "review_entity_edit", "review_finish"],
          paths: { raw_dir: "/tmp/raw", reviews_dir: "/tmp/reviews" }
        });
      }
      if (url.includes("/api/review/queue")) {
        return Response.json(queuePayload);
      }
      if (url.includes("/api/review/source/api-source/finish") && init?.method === "PATCH") {
        return new Response("conflict", { status: 409, statusText: "Conflict" });
      }
      if (url.includes("/api/review/source/api-source")) {
        return Response.json(sourcePayload);
      }
      return new Response("not found", { status: 404 });
    });
    render(<App />);

    await screen.findByText("API summary");
    await userEvent.click(screen.getByRole("button", { name: "Finish as approved" }));

    expect(await screen.findByText(/Finish failed/)).toBeInTheDocument();
    expect(await screen.findByRole("heading", { name: "API Article" })).toBeInTheDocument();
  });

  it("replaces the selected source when filters remove the current selection", async () => {
    render(<App />);

    expect(await screen.findByText("API summary")).toBeInTheDocument();

    await userEvent.selectOptions(screen.getByLabelText("Status"), "finished");

    expect(await screen.findByRole("heading", { name: "Finished Article" })).toBeInTheDocument();
    expect(await screen.findByText("Finished summary")).toBeInTheDocument();
    expect(screen.queryByText("API summary")).not.toBeInTheDocument();
  });

  it("renders expanded entity groups and source-specific insights", async () => {
    const fullCoverageSourcePayload = {
      ...sourcePayload,
      entities: buildEntityGroups([
        {
          group: "topics",
          label: "Topics",
          section: "wiki_entities",
          items: sourcePayload.entities.topics
        },
        {
          group: "how_to",
          label: "How-tos",
          section: "wiki_entities",
          items: [
            makeEntity(0, "How to cache prompts", {
              description: "Cache repeated prefixes.",
              render_category: "how_to"
            })
          ]
        },
        {
          group: "tools",
          label: "Tools",
          section: "wiki_entities",
          items: [
            makeEntity(0, "Prompt cache", {
              description: "Caching tool.",
              render_category: "tool"
            })
          ]
        },
        {
          group: "implementation_studies",
          label: "Implementation studies",
          section: "source_specific_insights",
          items: [
            makeEntity(0, "Telecom voicebot study", {
              description: "Evaluation at scale.",
              render_category: "impl_study",
              render_mode: "individual"
            })
          ]
        },
        {
          group: "signals",
          label: "Signals",
          section: "source_specific_insights",
          items: [
            makeEntity(0, "Signal headline", {
              description: "Signal summary.",
              render_category: "signal",
              render_mode: "individual"
            })
          ]
        }
      ])
    };
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/config")) {
        return Response.json(configPayload);
      }
      if (url.includes("/api/review/queue")) {
        return Response.json({
          ...queuePayload,
          items: [{ ...queuePayload.items[1], entity_counts: { ...emptyEntityCounts, topics: 1, how_to: 1, tools: 1, implementation_studies: 1, signals: 1 } }]
        });
      }
      if (url.includes("/api/review/source/api-source")) {
        return Response.json(fullCoverageSourcePayload);
      }
      return new Response("not found", { status: 404 });
    });
    render(<App />);

    expect(await screen.findByText("How to cache prompts")).toBeInTheDocument();
    expect(screen.getByText("Prompt cache")).toBeInTheDocument();
    expect(screen.getByText("Source-specific insights")).toBeInTheDocument();
    expect(screen.getByText("Telecom voicebot study")).toBeInTheDocument();
    expect(screen.getByText("Signal headline")).toBeInTheDocument();
    expect(screen.getByText("Topics 1")).toBeInTheDocument();
    expect(screen.getByText("How-tos 1")).toBeInTheDocument();
    expect(within(await screen.findByLabelText("Source list")).getByText(/5 entities/)).toBeInTheDocument();
  });

  it("shows full extraction for glossary and how-to entities", async () => {
    const multiEntitySource = {
      ...sourcePayload,
      entities: buildEntityGroups([
        {
          group: "glossary",
          label: "Glossary",
          section: "wiki_entities",
          items: [
            makeEntity(0, "RAG", {
              description: "Retrieval-augmented generation.",
              render_category: "glossary",
              detail_scalars: [
                { label: "Definition", body: "Retrieval-augmented generation." },
                { label: "Extended explanation", body: "Combines search with generation." }
              ]
            })
          ]
        },
        {
          group: "how_to",
          label: "How-tos",
          section: "wiki_entities",
          items: [
            makeEntity(0, "How to cache prompts", {
              description: "Reuse stable prefixes.",
              render_category: "how_to",
              detail_scalars: [
                { label: "Answer summary", body: "Reuse stable prefixes." },
                { label: "Caveats", body: "Cache invalidation still matters." }
              ],
              detail_lists: [{ label: "Implementation steps", items: ["Identify prefix"] }]
            })
          ]
        }
      ])
    };
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/config")) {
        return Response.json(configPayload);
      }
      if (url.includes("/api/review/queue")) {
        return Response.json({ ...queuePayload, items: [queuePayload.items[1]] });
      }
      if (url.includes("/api/review/source/api-source")) {
        return Response.json(multiEntitySource);
      }
      return new Response("not found", { status: 404 });
    });
    render(<App />);

    expect(await screen.findByText("RAG")).toBeInTheDocument();
    expect(screen.getByText("How to cache prompts")).toBeInTheDocument();
    expect(screen.getAllByText(/Full extraction/).length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText("Combines search with generation.")).toBeInTheDocument();
    expect(screen.getByText("Cache invalidation still matters.")).toBeInTheDocument();
    expect(screen.getByText("Identify prefix")).toBeInTheDocument();
  });

  it("shows full entity extraction on demand", async () => {
    const fullExtractionSource = {
      ...sourcePayload,
      entities: buildEntityGroups([
        {
          group: "topics",
          label: "Topics",
          section: "wiki_entities",
          items: [
            makeEntity(0, "API Topic", {
              description: "Topic description",
              tags: ["api"],
              detail_scalars: [
                { label: "Knowledge summary", body: "Topic description" },
                { label: "Operational insight", body: "Reuse durable context." },
                { label: "Relevance note", body: "Central to agent systems." },
                { label: "Supporting snippet", body: "Quoted evidence." }
              ],
              detail_lists: [{ label: "Key points", items: ["Point A", "Point B"] }]
            })
          ]
        }
      ])
    };
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/config")) {
        return Response.json(configPayload);
      }
      if (url.includes("/api/review/queue")) {
        return Response.json({ ...queuePayload, items: [queuePayload.items[1]] });
      }
      if (url.includes("/api/review/source/api-source")) {
        return Response.json(fullExtractionSource);
      }
      return new Response("not found", { status: 404 });
    });
    render(<App />);

    expect(await screen.findByText("API Topic")).toBeInTheDocument();
    const summary = screen.getByText("Full extraction (5)");
    const details = summary.closest("details");
    expect(details).not.toBeNull();
    expect(details).not.toHaveAttribute("open");
    await userEvent.click(summary);
    expect(details).toHaveAttribute("open");
    expect(screen.getByText("Reuse durable context.")).toBeInTheDocument();
    expect(screen.getByText("Central to agent systems.")).toBeInTheDocument();
    expect(screen.getByText("Quoted evidence.")).toBeInTheDocument();
    expect(screen.getByText("Point A")).toBeInTheDocument();
    expect(screen.getByText("Point B")).toBeInTheDocument();
  });

  it("edits a how-to through the existing entity endpoint", async () => {
    const howToSourcePayload = {
      ...sourcePayload,
      entities: buildEntityGroups([
        {
          group: "how_to",
          label: "How-tos",
          section: "wiki_entities",
          items: [
            makeEntity(0, "How to cache prompts", {
              description: "Cache repeated prefixes.",
              render_category: "how_to"
            })
          ]
        }
      ])
    };
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/api/config")) {
        return Response.json(configPayload);
      }
      if (url.includes("/api/review/source/api-source/entity") && init?.method === "PATCH") {
        return Response.json({
          ...entityEditResponse,
          group: "how_to",
          source: {
            ...howToSourcePayload,
            entities: buildEntityGroups([
              {
                group: "how_to",
                label: "How-tos",
                section: "wiki_entities",
                items: [
                  makeEntity(0, "Edited how-to", {
                    description: "Edited answer.",
                    render_category: "how_to"
                  })
                ]
              }
            ])
          }
        });
      }
      if (url.includes("/api/review/queue")) {
        return Response.json({ ...queuePayload, items: [queuePayload.items[1]] });
      }
      if (url.includes("/api/review/source/api-source")) {
        return Response.json(howToSourcePayload);
      }
      return new Response("not found", { status: 404 });
    });
    render(<App />);

    await userEvent.click(await screen.findByRole("button", { name: "Edit How to cache prompts" }));
    await userEvent.clear(screen.getByLabelText("Entity title"));
    await userEvent.type(screen.getByLabelText("Entity title"), "Edited how-to");
    await userEvent.click(screen.getByRole("button", { name: "Save entity" }));

    await waitFor(() => {
      expect(vi.mocked(fetch)).toHaveBeenCalledWith(
        "/api/review/source/api-source/entity",
        expect.objectContaining({
          body: JSON.stringify({
            group: "how_to",
            index: 0,
            title: "Edited how-to"
          }),
          method: "PATCH"
        })
      );
    });
    expect(await screen.findByText("Edited how-to")).toBeInTheDocument();
  });

  it("hides source-specific insights from the default list until show rejected is enabled", async () => {
    const hiddenInsightPayload = {
      ...sourcePayload,
      entities: buildEntityGroups([
        {
          group: "signals",
          label: "Signals",
          section: "source_specific_insights",
          items: [
            makeEntity(0, "Hidden signal", {
              description: "Hidden summary.",
              hidden: true,
              render_category: "signal",
              render_mode: "individual"
            })
          ]
        }
      ])
    };
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/api/config")) {
        return Response.json(configPayload);
      }
      if (url.includes("/api/review/source/api-source/entity") && init?.method === "PATCH") {
        return Response.json({
          ...entityEditResponse,
          group: "signals",
          source: hiddenInsightPayload
        });
      }
      if (url.includes("/api/review/queue")) {
        return Response.json({ ...queuePayload, items: [queuePayload.items[1]] });
      }
      if (url.includes("/api/review/source/api-source")) {
        return Response.json(hiddenInsightPayload);
      }
      return new Response("not found", { status: 404 });
    });
    render(<App />);

    await waitFor(() => expect(screen.queryByText("Hidden signal")).not.toBeInTheDocument());
    await userEvent.click(await screen.findByLabelText("Show rejected entities (1)"));
    expect(await screen.findByText("Hidden signal")).toBeInTheDocument();
  });

  it("shows Review and Pipeline navigation and opens the pipeline page", async () => {
    render(<App />);

    expect(await screen.findByRole("navigation", { name: "Main navigation" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Review" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Pipeline" })).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Pipeline" }));

    expect(await screen.findByRole("heading", { name: "Pipeline Cockpit" })).toBeInTheDocument();
    expect(await screen.findByRole("button", { name: "Update Wiki" })).toBeInTheDocument();
    expect(screen.getByText("Advanced manual operations")).toBeInTheDocument();
  });

  it("shows an explicit pipeline backend error instead of empty recommendations", async () => {
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/config")) {
        return Response.json(configPayload);
      }
      if (url.includes("/api/review/tags")) {
        return Response.json(tagRegistryPayload);
      }
      if (url.includes("/api/review/queue")) {
        return Response.json(queuePayload);
      }
      if (url.includes("/api/review/source/api-source")) {
        return Response.json(sourcePayload);
      }
      if (url.includes("/api/ops/status")) {
        return new Response("offline", { status: 503, statusText: "Service Unavailable" });
      }
      if (url.includes("/api/ops/operations")) {
        return Response.json(pipelineOperationsPayload);
      }
      if (url.includes("/api/ops/runs")) {
        return Response.json(pipelineRunsPayload);
      }
      return new Response("not found", { status: 404 });
    });
    render(<App />);

    await userEvent.click(await screen.findByRole("button", { name: "Pipeline" }));

    expect(await screen.findByText("Error: Request failed: 404")).toBeInTheDocument();
    expect(screen.queryByText("No recommendations yet.")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Refresh status" })).toBeInTheDocument();
  });

  it("renders the pipeline cockpit with operator-oriented sections and visible run state", async () => {
    render(<App />);

    await userEvent.click(await screen.findByRole("button", { name: "Pipeline" }));
    await userEvent.click(await screen.findByText("Advanced manual operations"));

    expect(await screen.findByRole("heading", { name: "Check wiki health" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Preview or publish wiki" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Inspect synthesis candidates" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Run synthesis batch" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Run health check" })).toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: "Preview render" }).length).toBeGreaterThan(0);
    expect(screen.getByRole("button", { name: "Write render..." })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Recent runs" })).toBeInTheDocument();
    expect(screen.getAllByText("Failed").length).toBeGreaterThan(0);
  });

  it("confirms write and LLM operations with plain-language impact and labeled parameters", async () => {
    render(<App />);

    await userEvent.click(await screen.findByRole("button", { name: "Pipeline" }));
    await userEvent.click(await screen.findByRole("button", { name: "Run batch..." }));

    expect(await screen.findByRole("dialog", { name: "Confirm operation" })).toBeInTheDocument();
    expect(screen.getByText("This operation writes files and may call the LLM API.")).toBeInTheDocument();
    expect(screen.getByText("Limit: 5")).toBeInTheDocument();
    expect(screen.getByText("Pause between calls: 300")).toBeInTheDocument();
    expect(screen.getByText("Expected output: synthesis cache files and an operation run report.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Confirm and run" })).toBeInTheDocument();
  });
});
