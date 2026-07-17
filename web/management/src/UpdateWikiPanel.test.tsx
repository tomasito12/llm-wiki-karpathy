import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import UpdateWikiPanel from "./UpdateWikiPanel";
import * as api from "./api";

vi.mock("./api");

const availabilityPayload = {
  update_available: true,
  headline: "Wiki update available",
  detail_line: "42 stale syntheses · render needs refresh · no blocking errors",
  hints: ["42 stale syntheses are ready for the next update."],
  blocking_errors: [],
  can_start: true,
  collected_at: "2026-07-16T10:00:00Z"
};

const waitingWorkflow = {
  run_id: "20260716T170000Z-update-wiki",
  workflow_id: "update_wiki",
  status: "waiting_for_confirmation" as const,
  current_step: "synthesis_batch",
  headline: "Update Wiki started",
  started_at: "2026-07-16T17:00:00Z",
  finished_at: null,
  duration_seconds: null,
  parameters: {
    synthesis_batch_size: 5,
    synthesis_between_calls_seconds: 300,
    auto_confirm: false
  },
  steps: [
    {
      id: "status",
      label: "Status check",
      status: "succeeded" as const,
      writes: false,
      llm_calls: false,
      summary_lines: ["Wiki update available"],
      technical_stdout: "",
      technical_stderr: "",
      exit_code: 0
    },
    {
      id: "synthesis_planning",
      label: "Candidate planning",
      status: "succeeded" as const,
      writes: false,
      llm_calls: false,
      summary_lines: ["42 candidates found · 5 selected for this run"],
      technical_stdout: "",
      technical_stderr: "",
      exit_code: 0
    },
    {
      id: "synthesis_batch",
      label: "Synthesis batch",
      status: "waiting" as const,
      writes: true,
      llm_calls: true,
      summary_lines: [
        "Run 5 synthesis updates now?",
        "5 of 42 synthesis candidates will be processed."
      ],
      technical_stdout: "",
      technical_stderr: "",
      exit_code: null
    }
  ],
  pending_confirmation: {
    id: "synthesis_batch",
    title: "Run 5 synthesis updates now?",
    description: "This may call the OpenAI API and will write synthesis cache files.",
    confirm_label: "Run synthesis",
    skip_label: "Skip synthesis for now",
    summary_lines: ["5 of 42 synthesis candidates will be processed."]
  },
  report_path: "/tmp/knowledge/tmp/management_runs/20260716T170000Z-update-wiki.json"
};

describe("UpdateWikiPanel", () => {
  beforeEach(() => {
    vi.mocked(api.getUpdateWikiStatus).mockResolvedValue(availabilityPayload);
    vi.mocked(api.getActiveUpdateWikiRun).mockResolvedValue({ run: null });
  });

  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
    sessionStorage.clear();
  });

  it("shows the primary Update Wiki action and default batch size", async () => {
    render(<UpdateWikiPanel />);

    expect(await screen.findByRole("button", { name: "Update Wiki" })).toBeInTheDocument();
    expect(screen.getByLabelText("Synthesis batch size")).toHaveValue(5);
    expect(screen.getByLabelText("Pause between syntheses (seconds)")).toHaveValue(300);
    expect(screen.getByText("Wiki update available")).toBeInTheDocument();
  });

  it("renders passive hints without action buttons", async () => {
    render(<UpdateWikiPanel />);

    expect(await screen.findByText("Hints")).toBeInTheDocument();
    expect(
      screen.getByText("42 stale syntheses are ready for the next update.")
    ).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Plan synthesis refresh" })).not.toBeInTheDocument();
  });

  it("renders inline synthesis confirmation on the waiting step", async () => {
    vi.mocked(api.startUpdateWiki).mockResolvedValue({
      run_id: waitingWorkflow.run_id,
      workflow_id: "update_wiki",
      status: "waiting_for_confirmation"
    });
    vi.mocked(api.getUpdateWikiRun).mockResolvedValue(waitingWorkflow);

    render(<UpdateWikiPanel />);
    await screen.findByRole("button", { name: "Update Wiki" });
    await userEvent.click(screen.getByRole("button", { name: "Update Wiki" }));

    expect(await screen.findByText("Action required: confirm the highlighted step below to continue.")).toBeInTheDocument();
    expect(screen.getByText("Synthesis batch")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Run synthesis" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Skip synthesis for now" })).toBeInTheDocument();
  });

  it("restores an active workflow run on mount", async () => {
    vi.mocked(api.getActiveUpdateWikiRun).mockResolvedValue({ run: waitingWorkflow });

    render(<UpdateWikiPanel />);

    expect(await screen.findByText("Action required: confirm the highlighted step below to continue.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Run synthesis" })).toBeInTheDocument();
  });

  it("expands technical details within a workflow step", async () => {
    vi.mocked(api.startUpdateWiki).mockResolvedValue({
      run_id: waitingWorkflow.run_id,
      workflow_id: "update_wiki",
      status: "waiting_for_confirmation"
    });
    vi.mocked(api.getUpdateWikiRun).mockResolvedValue({
      ...waitingWorkflow,
      steps: [
        {
          ...waitingWorkflow.steps[0],
          technical_stdout: "status details"
        },
        ...waitingWorkflow.steps.slice(1)
      ]
    });

    render(<UpdateWikiPanel />);
    await screen.findByRole("button", { name: "Update Wiki" });
    await userEvent.click(screen.getByRole("button", { name: "Update Wiki" }));

    await userEvent.click(await screen.findByRole("button", { name: "Show technical details" }));
    expect(await screen.findByText("status details")).toBeInTheDocument();
  });

  it("rejects invalid batch sizes client-side", async () => {
    render(<UpdateWikiPanel />);
    await screen.findByRole("button", { name: "Update Wiki" });

    await userEvent.clear(screen.getByLabelText("Synthesis batch size"));
    await userEvent.type(screen.getByLabelText("Synthesis batch size"), "0");
    await userEvent.click(screen.getByRole("button", { name: "Update Wiki" }));

    expect(await screen.findByText("Synthesis batch size must be between 1 and 100.")).toBeInTheDocument();
    expect(api.startUpdateWiki).not.toHaveBeenCalled();
  });

  it("shows live synthesis progress while a workflow step is running", async () => {
    vi.mocked(api.startUpdateWiki).mockResolvedValue({
      run_id: "20260716T170500Z-update-wiki",
      workflow_id: "update_wiki",
      status: "running"
    });
    vi.mocked(api.getUpdateWikiRun).mockResolvedValue({
      ...waitingWorkflow,
      status: "running",
      pending_confirmation: null,
      steps: [
        ...waitingWorkflow.steps.slice(0, 2),
        {
          id: "synthesis_batch",
          label: "Synthesis batch",
          status: "running",
          writes: true,
          llm_calls: true,
          summary_lines: ["Synthesizing topic:one (1/5)"],
          technical_stdout: "",
          technical_stderr: "",
          exit_code: null,
          progress_current: 1,
          progress_total: 5,
          progress_message: "Synthesizing topic:one (1/5)",
          progress_lines: ["processing topic:one index=1 total=5"]
        }
      ]
    });

    render(<UpdateWikiPanel />);
    await screen.findByRole("button", { name: "Update Wiki" });
    await userEvent.click(screen.getByRole("button", { name: "Update Wiki" }));

    expect(await screen.findByText("Synthesizing topic:one (1/5)")).toBeInTheDocument();
    expect(screen.getByRole("progressbar", { name: "Synthesis batch progress" })).toBeInTheDocument();
  });

  it("passes between-calls seconds when starting Update Wiki", async () => {
    vi.mocked(api.startUpdateWiki).mockResolvedValue({
      run_id: waitingWorkflow.run_id,
      workflow_id: "update_wiki",
      status: "waiting_for_confirmation"
    });
    vi.mocked(api.getUpdateWikiRun).mockResolvedValue(waitingWorkflow);

    render(<UpdateWikiPanel />);
    await screen.findByRole("button", { name: "Update Wiki" });
    await userEvent.clear(screen.getByLabelText("Pause between syntheses (seconds)"));
    await userEvent.type(screen.getByLabelText("Pause between syntheses (seconds)"), "500");
    await userEvent.click(screen.getByRole("button", { name: "Update Wiki" }));

    expect(api.startUpdateWiki).toHaveBeenCalledWith({
      synthesis_batch_size: 5,
      synthesis_between_calls_seconds: 500,
      auto_confirm: false
    });
  });

  it("passes auto_confirm when the checkbox is enabled", async () => {
    vi.mocked(api.startUpdateWiki).mockResolvedValue({
      run_id: waitingWorkflow.run_id,
      workflow_id: "update_wiki",
      status: "running"
    });
    vi.mocked(api.getUpdateWikiRun).mockResolvedValue({
      ...waitingWorkflow,
      status: "running",
      pending_confirmation: null
    });

    render(<UpdateWikiPanel />);
    await screen.findByRole("button", { name: "Update Wiki" });
    await userEvent.click(screen.getByLabelText("Auto-approve synthesis and render write"));
    await userEvent.click(screen.getByRole("button", { name: "Update Wiki" }));

    await waitFor(() =>
      expect(api.startUpdateWiki).toHaveBeenCalledWith({
        synthesis_batch_size: 5,
        synthesis_between_calls_seconds: 300,
        auto_confirm: true
      })
    );
  });
});
