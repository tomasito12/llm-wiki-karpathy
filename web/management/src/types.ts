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
