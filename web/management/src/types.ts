export type ReviewStatus = "pending" | "in_progress" | "finished" | "incomplete";
export type QueueStatusFilter = ReviewStatus | "all";
export type ManagementReviewStatus =
  | "approved"
  | "needs_attention"
  | "skipped"
  | "reanalyze_requested";
export type ManagementDecisionFilter = ManagementReviewStatus | "not_reviewed" | "all";

export interface ConfigResponse {
  mode: "readonly";
  paths: Record<string, string>;
}

export interface EntityCounts {
  topics: number;
  glossary: number;
  trends: number;
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

export interface NormalizedEntity {
  title: string;
  description: string;
  tags: string[];
  evidence: string;
  raw: Record<string, unknown>;
}

export interface EntityGroups {
  topics: NormalizedEntity[];
  glossary: NormalizedEntity[];
  trends: NormalizedEntity[];
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
