export type ReviewStatus = "pending" | "in_progress" | "finished" | "incomplete";
export type QueueStatusFilter = ReviewStatus | "all";
export type ManagementReviewStatus =
  | "approved"
  | "needs_attention"
  | "skipped"
  | "reanalyze_requested";
export type ManagementDecisionFilter = ManagementReviewStatus | "not_reviewed" | "all";
export type EditableEntityGroup =
  | "topics"
  | "glossary"
  | "trends"
  | "how_to"
  | "tools"
  | "models"
  | "implementation_studies"
  | "signals"
  | "interview_insights";
export type EntitySection = "wiki_entities" | "source_specific_insights";
export type RenderMode = "merged" | "individual";
export type ReviewTagSource = "registry" | "reviews" | "graph";

export type ManagementWebMode = "write_enabled";

export interface ConfigResponse {
  mode: ManagementWebMode;
  capabilities: string[];
  paths: Record<string, string>;
}

export interface EntityCounts {
  topics: number;
  glossary: number;
  trends: number;
  how_to: number;
  tools: number;
  models: number;
  implementation_studies: number;
  signals: number;
  interview_insights: number;
}

export interface QueueCounts {
  total: number;
  pending: number;
  in_progress: number;
  finished: number;
  incomplete: number;
}

export interface DecisionCounts {
  not_reviewed: number;
  approved: number;
  needs_attention: number;
  skipped: number;
  reanalyze_requested: number;
}

export interface QueueItem {
  source_id: string;
  title: string;
  author: string;
  publication: string;
  published_date: string;
  category: string;
  status: ReviewStatus;
  stale: boolean | null;
  tags: string[];
  entity_counts: EntityCounts;
  review_json_path: string;
  raw_md_available: boolean;
  management_status: ManagementReviewStatus | null;
}

export interface QueueResponse {
  counts: QueueCounts;
  decision_counts: DecisionCounts;
  items: QueueItem[];
  limit: number;
  offset: number;
}

export interface SourceMetadata {
  title: string;
  author: string;
  publication: string;
  published_date: string;
  canonical_url: string;
  category: string;
  readwise_id: string;
}

export interface SourcePaths {
  raw_html: string;
  raw_md: string | null;
  review_json: string;
}

export interface SourceSummary {
  short: string;
  key_insights: string[];
}

export interface EntityDetailList {
  label: string;
  items: string[];
}

export interface NormalizedEntity {
  index: number;
  title: string;
  description: string;
  tags: string[];
  types: string[];
  evidence: string;
  hidden: boolean;
  render_category: string;
  render_mode: RenderMode;
  detail_lists: EntityDetailList[];
  raw: Record<string, unknown>;
}

export interface NormalizedEntityGroup {
  group: EditableEntityGroup;
  label: string;
  section: EntitySection;
  items: NormalizedEntity[];
}

export interface EntityGroups {
  topics: NormalizedEntity[];
  glossary: NormalizedEntity[];
  trends: NormalizedEntity[];
  groups: NormalizedEntityGroup[];
}

export interface ManagementReview {
  status: ManagementReviewStatus;
  reviewed_at: string;
  reviewed_by: string;
  notes: string;
}

export interface ManagementReviewRequest {
  status: ManagementReviewStatus;
  notes: string;
}

export interface ManagementDecisionResponse {
  source_id: string;
  management_review: ManagementReview;
  backup_path: string | null;
}

export interface EntityEditRequest {
  group: EditableEntityGroup;
  index: number;
  title?: string;
  description?: string;
  tags?: string[];
  hidden?: boolean;
}

export interface EntityEditResponse {
  source_id: string;
  group: EditableEntityGroup;
  index: number;
  backup_path: string;
  source: SourceDetailResponse;
}

export interface FinishReviewRequest {
  notes: string;
  force: boolean;
}

export interface FinishReviewResponse {
  source_id: string;
  management_review: ManagementReview;
  review_finished_at: string;
  backup_path: string;
}

export interface SourceDetailResponse {
  source_id: string;
  status: ReviewStatus;
  stale: boolean | null;
  metadata: SourceMetadata;
  paths: SourcePaths;
  summary: SourceSummary;
  tags: string[];
  entities: EntityGroups;
  management_review: ManagementReview | null;
  debug: {
    artifact: Record<string, unknown>;
  };
}

export interface RawSourceResponse {
  source_id: string;
  available: boolean;
  content: string;
  path: string | null;
}

export interface ReviewTagChoice {
  name: string;
  source: ReviewTagSource;
  usage_count: number;
}

export interface ReviewTagsResponse {
  tags: ReviewTagChoice[];
}

export type OperationRunStatus = "queued" | "running" | "succeeded" | "failed" | "cancelled";
export type OperationParameterType = "integer" | "boolean" | "float";

export interface OpsStatusResponse {
  status: Record<string, unknown>;
  collected_at: string;
  summary: string;
}

export interface OperationParameter {
  name: string;
  label: string;
  type: OperationParameterType;
  default: boolean | number;
  required?: boolean;
}

export interface OperationDefinition {
  id: string;
  label: string;
  description: string;
  writes: boolean;
  llm_calls: boolean;
  requires_confirmation: boolean;
  parameters: OperationParameter[];
}

export interface OperationsListResponse {
  operations: OperationDefinition[];
}

export interface StartOperationRequest {
  operation_id: string;
  parameters?: Record<string, boolean | number>;
  confirmed?: boolean;
}

export interface StartOperationResponse {
  run_id: string;
  operation_id: string;
  status: OperationRunStatus;
}

export interface OperationRun {
  run_id: string;
  operation_id: string;
  label: string;
  status: OperationRunStatus;
  parameters: Record<string, boolean | number>;
  command: string[];
  cwd: string;
  writes: boolean;
  llm_calls: boolean;
  started_at: string;
  finished_at: string | null;
  duration_seconds: number | null;
  exit_code: number | null;
  stdout_tail: string;
  stderr_tail: string;
  report_path: string | null;
}

export interface OperationRunListResponse {
  runs: OperationRun[];
}

export type WorkflowRunStatus =
  | "running"
  | "waiting_for_confirmation"
  | "succeeded"
  | "failed"
  | "stopped";
export type WorkflowStepStatus =
  | "pending"
  | "running"
  | "succeeded"
  | "failed"
  | "skipped"
  | "waiting";

export interface WorkflowPendingConfirmation {
  id: string;
  title: string;
  description: string;
  confirm_label: string;
  skip_label: string;
  summary_lines: string[];
}

export interface WorkflowStep {
  id: string;
  label: string;
  status: WorkflowStepStatus;
  writes: boolean;
  llm_calls: boolean;
  summary_lines: string[];
  technical_stdout: string;
  technical_stderr: string;
  exit_code: number | null;
  progress_current?: number | null;
  progress_total?: number | null;
  progress_message?: string | null;
  progress_lines?: string[];
}

export interface UpdateWikiWorkflowRun {
  run_id: string;
  workflow_id: string;
  status: WorkflowRunStatus;
  current_step: string;
  headline: string;
  started_at: string;
  finished_at: string | null;
  duration_seconds: number | null;
  parameters: {
    synthesis_batch_size: number;
    synthesis_between_calls_seconds: number;
    auto_confirm?: boolean;
  };
  steps: WorkflowStep[];
  pending_confirmation: WorkflowPendingConfirmation | null;
  report_path: string | null;
}

export interface UpdateWikiAvailabilityResponse {
  update_available: boolean;
  headline: string;
  detail_line: string;
  hints: string[];
  blocking_errors: string[];
  can_start: boolean;
  collected_at: string;
}

export interface StartUpdateWikiRequest {
  synthesis_batch_size: number;
  synthesis_between_calls_seconds: number;
  auto_confirm: boolean;
}

export interface ActiveUpdateWikiWorkflowResponse {
  run: UpdateWikiWorkflowRun | null;
}

export interface StartUpdateWikiResponse {
  run_id: string;
  workflow_id: string;
  status: WorkflowRunStatus;
}

export interface ConfirmUpdateWikiRequest {
  confirmation_id: string;
}

export interface UpdateWikiWorkflowRunListResponse {
  runs: UpdateWikiWorkflowRun[];
}
