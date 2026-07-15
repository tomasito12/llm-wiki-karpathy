import { useEffect, useMemo, useState } from "react";
import type { ReactElement } from "react";

import {
  finishReview,
  getConfig,
  getRawSource,
  getReviewQueue,
  getSourceDetail,
  updateReviewEntity,
  writeManagementDecision
} from "./api";
import "./styles.css";
import type {
  ConfigResponse,
  EditableEntityGroup,
  EntityCounts,
  EntityGroups,
  EntitySection,
  ManagementDecisionFilter,
  ManagementReview,
  ManagementReviewStatus,
  ManagementWebMode,
  NormalizedEntity,
  NormalizedEntityGroup,
  QueueItem,
  QueueResponse,
  QueueStatusFilter,
  RawSourceResponse,
  SourceDetailResponse
} from "./types";

const STATUS_OPTIONS: Array<{ value: QueueStatusFilter; label: string }> = [
  { value: "all", label: "All" },
  { value: "pending", label: "Needs analysis" },
  { value: "in_progress", label: "Ready for review" },
  { value: "finished", label: "Finished" },
  { value: "incomplete", label: "Incomplete" }
];
const DECISION_FILTER_OPTIONS: Array<{ value: ManagementDecisionFilter; label: string }> = [
  { value: "not_reviewed", label: "Not reviewed" },
  { value: "all", label: "All decisions" },
  { value: "approved", label: "Approved" },
  { value: "needs_attention", label: "Needs attention" },
  { value: "skipped", label: "Skipped" },
  { value: "reanalyze_requested", label: "Re-analysis requested" }
];

const ENTITY_SECTIONS: Array<{ section: EntitySection; title: string }> = [
  { section: "wiki_entities", title: "Wiki entities" },
  { section: "source_specific_insights", title: "Source-specific insights" }
];

const ENTITY_COUNT_LABELS: Array<{ key: keyof EntityCounts; label: string }> = [
  { key: "topics", label: "topics" },
  { key: "glossary", label: "glossary" },
  { key: "trends", label: "trends" },
  { key: "how_to", label: "how-tos" },
  { key: "tools", label: "tools" },
  { key: "models", label: "models" },
  { key: "implementation_studies", label: "studies" },
  { key: "signals", label: "signals" },
  { key: "interview_insights", label: "insights" }
];
const QUEUE_LIMIT = 250;
const DECISION_ACTIONS: Array<{ status: ManagementReviewStatus; label: string }> = [
  { status: "approved", label: "Approve article" },
  { status: "needs_attention", label: "Needs attention" },
  { status: "skipped", label: "Skip" },
  { status: "reanalyze_requested", label: "Request re-analysis" }
];

interface EntityEditDraft {
  group: EditableEntityGroup;
  index: number;
  title: string;
  description: string;
  tags: string;
  hidden: boolean;
}

export default function App(): ReactElement {
  const [config, setConfig] = useState<ConfigResponse | null>(null);
  const [queue, setQueue] = useState<QueueResponse | null>(null);
  const [source, setSource] = useState<SourceDetailResponse | null>(null);
  const [rawSource, setRawSource] = useState<RawSourceResponse | null>(null);
  const [selectedSourceId, setSelectedSourceId] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<QueueStatusFilter>("in_progress");
  const [decisionFilter, setDecisionFilter] = useState<ManagementDecisionFilter>("not_reviewed");
  const [query, setQuery] = useState("");
  const [rawOpen, setRawOpen] = useState(false);
  const [debugOpen, setDebugOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [decisionPending, setDecisionPending] = useState(false);
  const [decisionMessage, setDecisionMessage] = useState<string | null>(null);
  const [decisionError, setDecisionError] = useState<string | null>(null);
  const [finishPending, setFinishPending] = useState(false);
  const [finishMessage, setFinishMessage] = useState<string | null>(null);
  const [finishError, setFinishError] = useState<string | null>(null);
  const [showHidden, setShowHidden] = useState(false);
  const [entityDraft, setEntityDraft] = useState<EntityEditDraft | null>(null);
  const [entityPending, setEntityPending] = useState(false);
  const [entityMessage, setEntityMessage] = useState<string | null>(null);
  const [entityMessageKey, setEntityMessageKey] = useState<string | null>(null);
  const [entityError, setEntityError] = useState<string | null>(null);

  useEffect(() => {
    getConfig().then(setConfig).catch((err: unknown) => setError(String(err)));
  }, []);

  useEffect(() => {
    getReviewQueue({ status: statusFilter, decision: decisionFilter, q: query, limit: QUEUE_LIMIT })
      .then((payload) => {
        const sortedPayload = { ...payload, items: sortQueueItems(payload.items) };
        setQueue(sortedPayload);
        setSelectedSourceId((current) => {
          if (current && sortedPayload.items.some((item) => item.source_id === current)) {
            return current;
          }
          return sortedPayload.items[0]?.source_id ?? null;
        });
      })
      .catch((err: unknown) => setError(String(err)));
  }, [decisionFilter, query, statusFilter]);

  useEffect(() => {
    if (!selectedSourceId) {
      setSource(null);
      return;
    }
    setRawOpen(false);
    setDebugOpen(false);
    setRawSource(null);
    setShowHidden(false);
    setEntityDraft(null);
    setEntityMessage(null);
    setEntityMessageKey(null);
    setEntityError(null);
    setFinishMessage(null);
    setFinishError(null);
    getSourceDetail(selectedSourceId).then(setSource).catch((err: unknown) => setError(String(err)));
  }, [selectedSourceId]);

  const selectedIndex = useMemo(() => {
    if (!queue || !selectedSourceId) {
      return -1;
    }
    return queue.items.findIndex((item) => item.source_id === selectedSourceId);
  }, [queue, selectedSourceId]);

  const visibleTotal = queue?.items.length ?? 0;

  function moveSelection(direction: -1 | 1): void {
    if (!queue || selectedIndex < 0) {
      return;
    }
    const next = queue.items[selectedIndex + direction];
    if (next) {
      setSelectedSourceId(next.source_id);
    }
  }

  function openRawSource(): void {
    if (!source) {
      return;
    }
    setRawOpen((current) => !current);
    if (!rawSource) {
      getRawSource(source.source_id)
        .then(setRawSource)
        .catch((err: unknown) => setError(String(err)));
    }
  }

  async function reloadSelectedSource(sourceId: string): Promise<void> {
    const queuePayload = await getReviewQueue({
      status: statusFilter,
      decision: decisionFilter,
      q: query,
      limit: QUEUE_LIMIT
    });
    const sortedPayload = { ...queuePayload, items: sortQueueItems(queuePayload.items) };
    setQueue(sortedPayload);
    const nextSourceId = sortedPayload.items.some((item) => item.source_id === sourceId)
      ? sourceId
      : (sortedPayload.items[0]?.source_id ?? null);
    setSelectedSourceId(nextSourceId);
    if (!nextSourceId) {
      setSource(null);
      setRawSource(null);
      setDecisionMessage(null);
      return;
    }
    if (nextSourceId !== sourceId) {
      setDecisionMessage(null);
    }
    setSource(await getSourceDetail(nextSourceId));
  }

  async function writeDecision(status: ManagementReviewStatus): Promise<void> {
    if (!source) {
      return;
    }
    setDecisionPending(true);
    setDecisionMessage(null);
    setDecisionError(null);
    try {
      const response = await writeManagementDecision(source.source_id, { status, notes: "" });
      setDecisionMessage(`Decision saved: ${response.management_review.status}`);
      try {
        await reloadSelectedSource(source.source_id);
      } catch (err: unknown) {
        setDecisionError(`Refresh failed: ${err instanceof Error ? err.message : String(err)}`);
      }
    } catch (err: unknown) {
      setDecisionError(`Decision failed: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setDecisionPending(false);
    }
  }

  async function finishCurrentReview(): Promise<void> {
    if (!source) {
      return;
    }
    setFinishPending(true);
    setFinishMessage(null);
    setFinishError(null);
    try {
      await finishReview(source.source_id, { notes: "", force: false });
      setFinishMessage("Review finished.");
      try {
        await reloadSelectedSource(source.source_id);
      } catch (err: unknown) {
        setFinishError(`Refresh failed: ${err instanceof Error ? err.message : String(err)}`);
      }
    } catch (err: unknown) {
      setFinishError(`Finish failed: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setFinishPending(false);
    }
  }

  function startEntityEdit(group: EditableEntityGroup, item: NormalizedEntity): void {
    setEntityDraft({
      group,
      index: item.index,
      title: item.title,
      description: item.description,
      tags: item.tags.join(", "),
      hidden: item.hidden
    });
    setEntityMessage(null);
    setEntityMessageKey(null);
    setEntityError(null);
  }

  async function saveEntityEdit(): Promise<void> {
    if (!source || !entityDraft) {
      return;
    }
    const validationError = entityDraftError(entityDraft);
    if (validationError) {
      setEntityError(validationError);
      return;
    }
    setEntityPending(true);
    setEntityMessage(null);
    setEntityError(null);
    try {
      const originalEntity = entityForDraft(source.entities, entityDraft);
      const response = await updateReviewEntity(
        source.source_id,
        buildEntityEditPayload(entityDraft, originalEntity)
      );
      const queuePayload = await getReviewQueue({
        status: statusFilter,
        decision: decisionFilter,
        q: query,
        limit: QUEUE_LIMIT
      });
      const sortedPayload = { ...queuePayload, items: sortQueueItems(queuePayload.items) };
      setQueue(sortedPayload);
      const nextSourceId = sortedPayload.items.some((item) => item.source_id === source.source_id)
        ? source.source_id
        : (sortedPayload.items[0]?.source_id ?? null);
      setSelectedSourceId(nextSourceId);
      if (!nextSourceId) {
        setSource(null);
      } else if (nextSourceId === source.source_id) {
        setSource(response.source);
      } else {
        setSource(await getSourceDetail(nextSourceId));
      }
      setEntityMessageKey(entityKey(entityDraft.group, entityDraft.index));
      setEntityDraft(null);
      setEntityMessage("Entity saved.");
    } catch (err: unknown) {
      setEntityError(`Entity save failed: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setEntityPending(false);
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <h1>Review Workspace</h1>
          <p>Batch review for pre-analyzed Readwise sources</p>
        </div>
        <div className="mode-pill">{managementModeLabel(config?.mode)}</div>
      </header>

      {error ? <div className="error-banner">{error}</div> : null}

      <main className="workspace">
        <aside className="queue-panel">
          <section className="panel-card">
            <h2>Queue</h2>
            <label>
              Status
              <select
                value={statusFilter}
                onChange={(event) => setStatusFilter(event.target.value as QueueStatusFilter)}
              >
                {STATUS_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Decision
              <select
                value={decisionFilter}
                onChange={(event) =>
                  setDecisionFilter(event.target.value as ManagementDecisionFilter)
                }
              >
                {DECISION_FILTER_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
            <DecisionCountsSummary queue={queue} decisionFilter={decisionFilter} />
            <label>
              Search
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Title, source id, tag"
              />
            </label>
          </section>

          <QueueCountsCard queue={queue} />

          <section className="source-list" aria-label="Source list">
            {queue?.items.map((item) => (
              <button
                className={item.source_id === selectedSourceId ? "source-row active" : "source-row"}
                key={item.source_id}
                onClick={() => setSelectedSourceId(item.source_id)}
              >
                <span>{item.title}</span>
                <small>
                  {item.published_date || "No date"} · {formatEntityCounts(item.entity_counts)}
                </small>
                {item.management_status ? (
                  <small className={`management-badge ${managementStatusClass(item.management_status)}`}>
                    {managementStatusLabel(item.management_status)}
                  </small>
                ) : null}
              </button>
            ))}
            {queue?.items.length === 0 ? <p className="empty-state">No sources match.</p> : null}
          </section>
        </aside>

        <section className="review-panel">
          {source ? (
            <>
              <SourceHeader
                source={source}
                selectedIndex={selectedIndex}
                visibleTotal={visibleTotal}
                canMovePrevious={selectedIndex > 0}
                canMoveNext={Boolean(
                  queue && selectedIndex >= 0 && selectedIndex < queue.items.length - 1
                )}
                onMovePrevious={() => moveSelection(-1)}
                onMoveNext={() => moveSelection(1)}
                decisionPending={decisionPending}
                decisionMessage={decisionMessage}
                decisionError={decisionError}
                finishPending={finishPending}
                finishMessage={finishMessage}
                finishError={finishError}
                onDecision={writeDecision}
                onFinish={() => void finishCurrentReview()}
              />
              <SummaryCard source={source} />
              <TagCloud tags={source.tags} />
              <EntitySections
                editDraft={entityDraft}
                entityError={entityError}
                entityMessage={entityMessage}
                entityMessageKey={entityMessageKey}
                entityPending={entityPending}
                entities={source.entities}
                onCancelEdit={() => setEntityDraft(null)}
                onDraftChange={setEntityDraft}
                onSaveEdit={() => void saveEntityEdit()}
                onStartEdit={startEntityEdit}
                showHidden={showHidden}
                onShowHiddenChange={setShowHidden}
              />
              <div className="utility-actions">
                <button onClick={openRawSource}>
                  {rawOpen ? "Hide raw source" : "Show raw source"}
                </button>
                <button onClick={() => setDebugOpen((current) => !current)}>
                  {debugOpen ? "Hide debug JSON" : "Show debug JSON"}
                </button>
              </div>
              {rawOpen ? <RawDrawer rawSource={rawSource} /> : null}
              {debugOpen ? (
                <pre className="debug-json">{JSON.stringify(source.debug.artifact, null, 2)}</pre>
              ) : null}
            </>
          ) : (
            <div className="empty-state">Select a source to inspect its review artifact.</div>
          )}

          <details className="path-details">
            <summary>Paths</summary>
            <p>{config?.paths.raw_dir ?? "Loading raw path..."}</p>
            <p>{config?.paths.reviews_dir ?? "Loading reviews path..."}</p>
          </details>
        </section>
      </main>
    </div>
  );
}

function statusLabel(status: QueueStatusFilter): string {
  if (status === "pending") {
    return "Needs analysis";
  }
  if (status === "in_progress") {
    return "Ready for review";
  }
  if (status === "all") {
    return "All";
  }
  return status.charAt(0).toUpperCase() + status.slice(1);
}

function managementStatusLabel(status: ManagementReviewStatus): string {
  if (status === "approved") {
    return "Approved";
  }
  if (status === "needs_attention") {
    return "Needs attention";
  }
  if (status === "skipped") {
    return "Skipped";
  }
  return "Re-analysis requested";
}

function managementStatusClass(status: ManagementReviewStatus): string {
  if (status === "approved") {
    return "management-approved";
  }
  if (status === "skipped") {
    return "management-skipped";
  }
  return "management-attention";
}

function countForDecisionFilter(queue: QueueResponse, decision: ManagementDecisionFilter): number {
  if (decision === "all") {
    const counts = queue.decision_counts;
    return (
      counts.not_reviewed +
      counts.approved +
      counts.needs_attention +
      counts.skipped +
      counts.reanalyze_requested
    );
  }
  return queue.decision_counts[decision];
}

function managementModeLabel(mode: ManagementWebMode | undefined): string {
  if (mode === "write_enabled") {
    return "Write enabled";
  }
  return "Loading...";
}

function sortQueueItems(items: QueueItem[]): QueueItem[] {
  return [...items].sort((left, right) => {
    const leftDate = left.published_date || "9999-12-31";
    const rightDate = right.published_date || "9999-12-31";
    if (leftDate !== rightDate) {
      return leftDate.localeCompare(rightDate);
    }
    return left.title.localeCompare(right.title);
  });
}

function entityKey(group: EditableEntityGroup, index: number): string {
  return `${group}:${index}`;
}

function formatEntityCounts(counts: EntityCounts): string {
  const parts = ENTITY_COUNT_LABELS.filter(({ key }) => counts[key] > 0).map(
    ({ key, label }) => `${counts[key]} ${label}`
  );
  return parts.length > 0 ? parts.join(" · ") : "0 entities";
}

function entityGroupItems(entities: EntityGroups, group: EditableEntityGroup): NormalizedEntity[] {
  return entities.groups.find((entry) => entry.group === group)?.items ?? [];
}

function isHiddenEntity(item: NormalizedEntity): boolean {
  return item.hidden;
}

function parseTagInput(input: string): string[] {
  if (!input.trim()) {
    return [];
  }
  return input.split(",").map((tag) => tag.trim());
}

function entityDraftError(draft: EntityEditDraft): string | null {
  if (!draft.title.trim()) {
    return "Title cannot be empty.";
  }
  if (draft.description !== "" && !draft.description.trim()) {
    return "Description cannot be empty.";
  }
  if (parseTagInput(draft.tags).some((tag) => tag === "")) {
    return "Tags cannot contain empty values.";
  }
  return null;
}

function entityForDraft(
  entities: EntityGroups,
  draft: EntityEditDraft
): NormalizedEntity | null {
  return entityGroupItems(entities, draft.group).find((item) => item.index === draft.index) ?? null;
}

function buildEntityEditPayload(
  draft: EntityEditDraft,
  original: NormalizedEntity | null
): {
  group: EditableEntityGroup;
  index: number;
  title?: string;
  description?: string;
  tags?: string[];
  hidden?: boolean;
} {
  const payload: {
    group: EditableEntityGroup;
    index: number;
    title?: string;
    description?: string;
    tags?: string[];
    hidden?: boolean;
  } = {
    group: draft.group,
    index: draft.index
  };
  if (!original || draft.title !== original.title) {
    payload.title = draft.title.trim();
  }
  if (!original || draft.description !== original.description) {
    payload.description = draft.description.trim();
  }
  if (!original || draft.tags !== original.tags.join(", ")) {
    payload.tags = parseTagInput(draft.tags);
  }
  if (!original || draft.hidden !== isHiddenEntity(original)) {
    payload.hidden = draft.hidden;
  }
  return payload;
}

function entityDraftUnchanged(draft: EntityEditDraft, item: NormalizedEntity): boolean {
  return (
    draft.title === item.title &&
    draft.description === item.description &&
    draft.tags === item.tags.join(", ") &&
    draft.hidden === isHiddenEntity(item)
  );
}

function DecisionCountsSummary({
  queue,
  decisionFilter
}: {
  queue: QueueResponse | null;
  decisionFilter: ManagementDecisionFilter;
}): ReactElement {
  if (!queue) {
    return <p className="decision-counts">Loading decision counts...</p>;
  }
  const selectedCount = countForDecisionFilter(queue, decisionFilter);
  return (
    <p className="decision-counts">
      {queue.decision_counts.not_reviewed} not reviewed · {queue.decision_counts.approved} approved ·{" "}
      {queue.decision_counts.needs_attention} needs attention · selected {selectedCount}
    </p>
  );
}

function QueueCountsCard({ queue }: { queue: QueueResponse | null }): ReactElement {
  return (
    <section className="counts-grid">
      <Metric label="Total" value={queue?.counts.total ?? 0} />
      <Metric label="Needs analysis" value={queue?.counts.pending ?? 0} />
      <Metric label="Ready for review" value={queue?.counts.in_progress ?? 0} />
      <Metric label="Finished" value={queue?.counts.finished ?? 0} />
      <Metric label="Incomplete" value={queue?.counts.incomplete ?? 0} />
    </section>
  );
}

function Metric({ label, value }: { label: string; value: number }): ReactElement {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function SourceHeader({
  source,
  selectedIndex,
  visibleTotal,
  canMovePrevious,
  canMoveNext,
  onMovePrevious,
  onMoveNext,
  decisionPending,
  decisionMessage,
  decisionError,
  finishPending,
  finishMessage,
  finishError,
  onDecision,
  onFinish
}: {
  source: SourceDetailResponse;
  selectedIndex: number;
  visibleTotal: number;
  canMovePrevious: boolean;
  canMoveNext: boolean;
  onMovePrevious: () => void;
  onMoveNext: () => void;
  decisionPending: boolean;
  decisionMessage: string | null;
  decisionError: string | null;
  finishPending: boolean;
  finishMessage: string | null;
  finishError: string | null;
  onDecision: (status: ManagementReviewStatus) => Promise<void>;
  onFinish: () => void;
}): ReactElement {
  return (
    <section className="source-header">
      <div>
        <p className="eyebrow">{source.metadata.publication || source.metadata.category || "Source"}</p>
        <h2>{source.metadata.title}</h2>
        <p className="source-byline">
          {source.metadata.author || "Unknown author"} · {source.metadata.published_date || "No date"}
        </p>
        <div className="status-row">
          <span>{statusLabel(source.status)}</span>
          <span>{source.stale === null ? "Stale unknown" : source.stale ? "Stale" : "Current"}</span>
          <span>Readwise {source.metadata.readwise_id || "unknown"}</span>
        </div>
        <ManagementDecisionState review={source.management_review} />
      </div>
      <div className="review-navigation">
        <span>{selectedIndex >= 0 ? `${selectedIndex + 1} / ${visibleTotal}` : "No source"}</span>
        <div className="button-row">
          <button disabled={!canMovePrevious} onClick={onMovePrevious}>
            Previous
          </button>
          <button disabled={!canMoveNext} onClick={onMoveNext}>
            Next
          </button>
        </div>
        <button className="primary-action" disabled={finishPending || decisionPending} onClick={onFinish}>
          Finish review
        </button>
        <div className="decision-actions" aria-label="Article decisions">
          {DECISION_ACTIONS.map((action) => (
            <button
              disabled={decisionPending || finishPending}
              key={action.status}
              onClick={() => void onDecision(action.status)}
            >
              {action.label}
            </button>
          ))}
        </div>
        {finishMessage ? <p className="success-message">{finishMessage}</p> : null}
        {finishError ? <p className="error-message">{finishError}</p> : null}
        {decisionMessage ? <p className="success-message">{decisionMessage}</p> : null}
        {decisionError ? <p className="error-message">{decisionError}</p> : null}
      </div>
    </section>
  );
}

function ManagementDecisionState({
  review
}: {
  review: ManagementReview | null;
}): ReactElement {
  if (!review) {
    return <p className="management-review-state">Decision: Not reviewed</p>;
  }
  return (
    <div className={`management-review-state ${managementStatusClass(review.status)}`}>
      <strong>Decision: {managementStatusLabel(review.status)}</strong>
      <span>Reviewed by {review.reviewed_by}</span>
      <span>{review.reviewed_at}</span>
      {review.notes ? <p>{review.notes}</p> : null}
    </div>
  );
}

function SummaryCard({ source }: { source: SourceDetailResponse }): ReactElement {
  const easyRead = source.summary.short || "No easy read available.";
  return (
    <section className="review-card easy-read-card">
      <h3>Easy Read</h3>
      <p>{easyRead}</p>
      {source.summary.key_insights.length > 0 ? (
        <details>
          <summary>Key insights ({source.summary.key_insights.length})</summary>
          <ul>
            {source.summary.key_insights.map((insight) => (
              <li key={insight}>{insight}</li>
            ))}
          </ul>
        </details>
      ) : null}
    </section>
  );
}

function TagCloud({ tags }: { tags: string[] }): ReactElement {
  return (
    <section className="review-card">
      <h3>Tags</h3>
      <div className="tag-cloud">
        {tags.length > 0 ? tags.map((tag) => <span key={tag}>{tag}</span>) : <p>No tags found.</p>}
      </div>
    </section>
  );
}

function EntitySections({
  editDraft,
  entityError,
  entityMessage,
  entityMessageKey,
  entityPending,
  entities,
  onCancelEdit,
  onDraftChange,
  onSaveEdit,
  onStartEdit,
  showHidden,
  onShowHiddenChange
}: {
  editDraft: EntityEditDraft | null;
  entityError: string | null;
  entityMessage: string | null;
  entityMessageKey: string | null;
  entityPending: boolean;
  entities: EntityGroups;
  onCancelEdit: () => void;
  onDraftChange: (draft: EntityEditDraft) => void;
  onSaveEdit: () => void;
  onStartEdit: (group: EditableEntityGroup, item: NormalizedEntity) => void;
  showHidden: boolean;
  onShowHiddenChange: (showHidden: boolean) => void;
}): ReactElement {
  return (
    <section className="entity-workspace">
      <label className="inline-toggle">
        <input
          checked={showHidden}
          onChange={(event) => onShowHiddenChange(event.target.checked)}
          type="checkbox"
        />
        Show hidden
      </label>
      {ENTITY_SECTIONS.map((section) => (
        <EntitySectionBlock
          editDraft={editDraft}
          entityError={entityError}
          entityMessage={entityMessage}
          entityMessageKey={entityMessageKey}
          entityPending={entityPending}
          groups={entities.groups.filter((group) => group.section === section.section)}
          key={section.section}
          onCancelEdit={onCancelEdit}
          onDraftChange={onDraftChange}
          onSaveEdit={onSaveEdit}
          onStartEdit={onStartEdit}
          sectionTitle={section.title}
          showHidden={showHidden}
        />
      ))}
    </section>
  );
}

function EntitySectionBlock({
  editDraft,
  entityError,
  entityMessage,
  entityMessageKey,
  entityPending,
  groups,
  onCancelEdit,
  onDraftChange,
  onSaveEdit,
  onStartEdit,
  sectionTitle,
  showHidden
}: {
  editDraft: EntityEditDraft | null;
  entityError: string | null;
  entityMessage: string | null;
  entityMessageKey: string | null;
  entityPending: boolean;
  groups: NormalizedEntityGroup[];
  onCancelEdit: () => void;
  onDraftChange: (draft: EntityEditDraft) => void;
  onSaveEdit: () => void;
  onStartEdit: (group: EditableEntityGroup, item: NormalizedEntity) => void;
  sectionTitle: string;
  showHidden: boolean;
}): ReactElement | null {
  const visibleGroups = groups.filter((group) => {
    const visibleItems = showHidden
      ? group.items
      : group.items.filter((item) => !isHiddenEntity(item));
    return visibleItems.length > 0;
  });
  if (visibleGroups.length === 0) {
    return null;
  }
  return (
    <section
      className={
        sectionTitle === "Source-specific insights"
          ? "entity-section source-specific-section"
          : "entity-section"
      }
    >
      <h3 className="entity-section-title">{sectionTitle}</h3>
      <div className="entity-grid">
        {visibleGroups.map((group) => (
          <EntityGroup
            editDraft={editDraft}
            entityError={entityError}
            entityMessage={entityMessage}
            entityMessageKey={entityMessageKey}
            entityPending={entityPending}
            group={group.group}
            items={group.items}
            key={group.group}
            onCancelEdit={onCancelEdit}
            onDraftChange={onDraftChange}
            onSaveEdit={onSaveEdit}
            onStartEdit={onStartEdit}
            showHidden={showHidden}
            title={group.label}
          />
        ))}
      </div>
    </section>
  );
}

function EntityGroup({
  editDraft,
  entityError,
  entityMessage,
  entityMessageKey,
  entityPending,
  group,
  title,
  items,
  onCancelEdit,
  onDraftChange,
  onSaveEdit,
  onStartEdit,
  showHidden
}: {
  editDraft: EntityEditDraft | null;
  entityError: string | null;
  entityMessage: string | null;
  entityMessageKey: string | null;
  entityPending: boolean;
  group: EditableEntityGroup;
  title: string;
  items: NormalizedEntity[];
  onCancelEdit: () => void;
  onDraftChange: (draft: EntityEditDraft) => void;
  onSaveEdit: () => void;
  onStartEdit: (group: EditableEntityGroup, item: NormalizedEntity) => void;
  showHidden: boolean;
}): ReactElement {
  const visibleItems = showHidden ? items : items.filter((item) => !isHiddenEntity(item));
  if (visibleItems.length === 0) {
    return (
      <section className="empty-entity-row">
        <span>{title}</span>
        <small>No {title.toLowerCase()} extracted</small>
      </section>
    );
  }

  return (
    <section className="review-card entity-group">
      <h3>
        {title} <span>{visibleItems.length}</span>
      </h3>
      {visibleItems.map((item) => {
        const isEditing = entityKey(group, item.index) === (
          editDraft ? entityKey(editDraft.group, editDraft.index) : ""
        );
        return (
          <EntityCard
            editDraft={isEditing ? editDraft : null}
            entityError={isEditing ? entityError : null}
            entityMessage={entityKey(group, item.index) === entityMessageKey ? entityMessage : null}
            entityPending={entityPending}
            group={group}
            item={item}
            key={`${title}-${item.index}-${item.title}`}
            onCancelEdit={onCancelEdit}
            onDraftChange={onDraftChange}
            onSaveEdit={onSaveEdit}
            onStartEdit={onStartEdit}
          />
        );
      })}
    </section>
  );
}

function EntityCard({
  editDraft,
  entityError,
  entityMessage,
  entityPending,
  group,
  item,
  onCancelEdit,
  onDraftChange,
  onSaveEdit,
  onStartEdit
}: {
  editDraft: EntityEditDraft | null;
  entityError: string | null;
  entityMessage: string | null;
  entityPending: boolean;
  group: EditableEntityGroup;
  item: NormalizedEntity;
  onCancelEdit: () => void;
  onDraftChange: (draft: EntityEditDraft) => void;
  onSaveEdit: () => void;
  onStartEdit: (group: EditableEntityGroup, item: NormalizedEntity) => void;
}): ReactElement {
  const hidden = isHiddenEntity(item);
  if (editDraft) {
    const validationError = entityDraftError(editDraft);
    const unchanged = entityDraftUnchanged(editDraft, item);
    return (
      <article className="entity-card entity-editor">
        <label>
          Entity title
          <input
            disabled={entityPending}
            onChange={(event) => onDraftChange({ ...editDraft, title: event.target.value })}
            value={editDraft.title}
          />
        </label>
        <label>
          Entity description
          <textarea
            disabled={entityPending}
            onChange={(event) => onDraftChange({ ...editDraft, description: event.target.value })}
            value={editDraft.description}
          />
        </label>
        <label>
          Entity tags
          <input
            disabled={entityPending}
            onChange={(event) => onDraftChange({ ...editDraft, tags: event.target.value })}
            value={editDraft.tags}
          />
        </label>
        <label className="inline-toggle">
          <input
            checked={editDraft.hidden}
            disabled={entityPending}
            onChange={(event) => onDraftChange({ ...editDraft, hidden: event.target.checked })}
            type="checkbox"
          />
          Hidden
        </label>
        {validationError ? <p className="error-message inline">{validationError}</p> : null}
        {entityError ? <p className="error-message inline">{entityError}</p> : null}
        <div className="button-row">
          <button onClick={onCancelEdit} disabled={entityPending}>
            Cancel edit
          </button>
          <button
            disabled={entityPending || Boolean(validationError) || unchanged}
            onClick={onSaveEdit}
          >
            Save entity
          </button>
        </div>
      </article>
    );
  }
  return (
    <article className={hidden ? "entity-card hidden-entity" : "entity-card"}>
      <div className="entity-card-header">
        <h4>{item.title || "Untitled entity"}</h4>
        <button onClick={() => onStartEdit(group, item)}>Edit {item.title || "entity"}</button>
      </div>
      {hidden ? <span className="hidden-badge">Hidden</span> : null}
      {item.description ? <p>{item.description}</p> : null}
      {entityMessage ? <p className="success-message inline">{entityMessage}</p> : null}
      {item.tags.length > 0 ? (
        <div className="tag-cloud compact">
          {item.tags.map((tag) => (
            <span key={tag}>{tag}</span>
          ))}
        </div>
      ) : null}
      {item.types.length > 0 ? (
        <div className="tag-cloud compact">
          {item.types.map((type) => (
            <span className="type-chip" key={type}>
              {type}
            </span>
          ))}
        </div>
      ) : null}
      {item.detail_lists.map((detailList) => (
        <details className="entity-detail-list" key={detailList.label}>
          <summary>
            {detailList.label} ({detailList.items.length})
          </summary>
          <ul>
            {detailList.items.map((entry) => (
              <li key={entry}>{entry}</li>
            ))}
          </ul>
        </details>
      ))}
      {item.evidence ? (
        <details className="evidence-details">
          <summary>Evidence</summary>
          <blockquote>{item.evidence}</blockquote>
        </details>
      ) : null}
    </article>
  );
}

function RawDrawer({ rawSource }: { rawSource: RawSourceResponse | null }): ReactElement {
  if (!rawSource) {
    return <section className="drawer">Loading raw source...</section>;
  }
  return (
    <section className="drawer">
      <h3>Raw Source</h3>
      {rawSource.available ? <pre>{rawSource.content}</pre> : <p>Raw Markdown is unavailable.</p>}
    </section>
  );
}
