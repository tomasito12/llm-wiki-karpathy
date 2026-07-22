import { useEffect, useMemo, useState } from "react";
import type { ReactElement } from "react";

import {
  finishReview,
  getConfig,
  getRawSource,
  getReviewQueue,
  getReviewTags,
  getReviewTypes,
  getSourceDetail,
  updateReviewEntity,
  writeManagementDecision
} from "./api";
import "./styles.css";
import { TagPicker, normalizeTagSlug } from "./TagPicker";
import PipelineCockpit from "./PipelineCockpit";
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
  QueueCounts,
  QueueItem,
  QueueResponse,
  QueueStatusFilter,
  RawSourceResponse,
  ReviewStatus,
  ReviewTagChoice,
  SourceDetailResponse
} from "./types";

const STATUS_OPTIONS: Array<{ value: QueueStatusFilter; label: string }> = [
  { value: "all", label: "All" },
  { value: "pending", label: "Needs analysis" },
  { value: "in_progress", label: "Ready to review" },
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
  { status: "needs_attention", label: "Needs attention" },
  { status: "skipped", label: "Skip" },
  { status: "reanalyze_requested", label: "Request re-analysis" }
];

type AppView = "review" | "pipeline";

interface EntityEditDraft {
  group: EditableEntityGroup;
  index: number;
  title: string;
  description: string;
  tags: string[];
  newTagNames: string[];
  types: string[];
  newTypeNames: string[];
}

export default function App(): ReactElement {
  const [activeView, setActiveView] = useState<AppView>("review");
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
  const [showRejected, setShowRejected] = useState(false);
  const [availableTags, setAvailableTags] = useState<ReviewTagChoice[]>([]);
  const [availableTypes, setAvailableTypes] = useState<ReviewTagChoice[]>([]);
  const [tagsLoading, setTagsLoading] = useState(false);
  const [typesLoading, setTypesLoading] = useState(false);
  const [entityDraft, setEntityDraft] = useState<EntityEditDraft | null>(null);
  const [entityPending, setEntityPending] = useState(false);
  const [entityMessage, setEntityMessage] = useState<string | null>(null);
  const [entityMessageKey, setEntityMessageKey] = useState<string | null>(null);
  const [entityError, setEntityError] = useState<string | null>(null);

  useEffect(() => {
    getConfig().then(setConfig).catch((err: unknown) => setError(String(err)));
  }, []);

  useEffect(() => {
    if (!entityDraft) {
      return;
    }
    setTagsLoading(true);
    getReviewTags(entityDraft.group)
      .then((response) => setAvailableTags(response.tags))
      .catch((err: unknown) => setEntityError(String(err)))
      .finally(() => setTagsLoading(false));
    if (entityDraft.group === "tools") {
      setTypesLoading(true);
      getReviewTypes("tools")
        .then((response) => setAvailableTypes(response.types))
        .catch((err: unknown) => setEntityError(String(err)))
        .finally(() => setTypesLoading(false));
    } else {
      setAvailableTypes([]);
      setTypesLoading(false);
    }
  }, [entityDraft?.group, entityDraft?.index]);

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
    setShowRejected(false);
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
      tags: [...item.tags],
      newTagNames: [],
      types: [...item.types],
      newTypeNames: []
    });
    setEntityMessage(null);
    setEntityMessageKey(null);
    setEntityError(null);
  }

  async function refreshAfterEntityChange(
    sourceId: string,
    responseSource: SourceDetailResponse,
    entityKeyValue: string
  ): Promise<void> {
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
    } else if (nextSourceId === sourceId) {
      setSource(responseSource);
    } else {
      setSource(await getSourceDetail(nextSourceId));
    }
    setEntityMessageKey(entityKeyValue);
    setEntityDraft(null);
  }

  async function updateEntityRejectedState(
    group: EditableEntityGroup,
    index: number,
    hidden: boolean
  ): Promise<void> {
    if (!source) {
      return;
    }
    setEntityPending(true);
    setEntityMessage(null);
    setEntityError(null);
    try {
      const response = await updateReviewEntity(source.source_id, { group, index, hidden });
      await refreshAfterEntityChange(
        source.source_id,
        response.source,
        entityKey(group, index)
      );
      setEntityMessage(hidden ? "Entity rejected." : "Entity restored.");
    } catch (err: unknown) {
      setEntityError(
        `${hidden ? "Reject" : "Restore"} failed: ${err instanceof Error ? err.message : String(err)}`
      );
    } finally {
      setEntityPending(false);
    }
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
      await refreshAfterEntityChange(
        source.source_id,
        response.source,
        entityKey(entityDraft.group, entityDraft.index)
      );
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
          <h1>{activeView === "review" ? "Review Workspace" : "Pipeline Cockpit"}</h1>
          <p>
            {activeView === "review"
              ? "Batch review for pre-analyzed Readwise sources"
              : "Status, recommendations, and safe pipeline operations"}
          </p>
          <nav aria-label="Main navigation" className="app-nav">
            <button
              className={activeView === "review" ? "nav-link active" : "nav-link"}
              onClick={() => setActiveView("review")}
              type="button"
            >
              Review
            </button>
            <button
              className={activeView === "pipeline" ? "nav-link active" : "nav-link"}
              onClick={() => setActiveView("pipeline")}
              type="button"
            >
              Pipeline
            </button>
          </nav>
        </div>
        <div className="mode-pill">{managementModeLabel(config?.mode)}</div>
      </header>

      {activeView === "pipeline" ? (
        <div className="app-view">
          <PipelineCockpit />
        </div>
      ) : (
        <div aria-hidden="true" className="app-view app-view-hidden">
          <PipelineCockpit />
        </div>
      )}

      {activeView === "review" ? (
        <>
      {error ? <div className="error-banner">{error}</div> : null}

      <main className="workspace">
        <aside className="queue-panel">
          <section className="panel-card queue-controls">
            <div className="queue-controls-header">
              <h2>Queue</h2>
              {queue ? <QueueStatusSummary counts={queue.counts} /> : null}
            </div>
            <div className="queue-filter-grid">
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
            </div>
            <DecisionCountsSummary queue={queue} decisionFilter={decisionFilter} />
            <label className="queue-search">
              Search
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Title, source id, tag"
              />
            </label>
          </section>

          <section className="source-list" aria-label="Source list">
            {queue?.items.map((item) => (
              <button
                className={item.source_id === selectedSourceId ? "source-row active" : "source-row"}
                key={item.source_id}
                onClick={() => setSelectedSourceId(item.source_id)}
              >
                <span>{item.title}</span>
                <small>
                  {item.published_date || "No date"}
                  {formatQueueEntityTotal(item.entity_counts)
                    ? ` · ${formatQueueEntityTotal(item.entity_counts)}`
                    : ""}
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
              <ExtractionOverview entities={source.entities} />
              <TagCloud tags={source.tags} />
              <EntitySections
                availableTags={availableTags}
                availableTypes={availableTypes}
                editDraft={entityDraft}
                entityError={entityError}
                entityMessage={entityMessage}
                entityMessageKey={entityMessageKey}
                entityPending={entityPending}
                entities={source.entities}
                onCancelEdit={() => setEntityDraft(null)}
                onDraftChange={setEntityDraft}
                onReject={(group, index) => void updateEntityRejectedState(group, index, true)}
                onRestore={(group, index) => void updateEntityRejectedState(group, index, false)}
                onSaveEdit={() => void saveEntityEdit()}
                onStartEdit={startEntityEdit}
                showRejected={showRejected}
                onShowRejectedChange={setShowRejected}
                tagsLoading={tagsLoading}
                typesLoading={typesLoading}
              />
              <div className="utility-actions secondary-utilities">
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
        </>
      ) : null}
    </div>
  );
}

function sourceReviewStatusLabel(status: ReviewStatus): string {
  if (status === "pending") {
    return "Needs analysis";
  }
  if (status === "in_progress") {
    return "Ready to review";
  }
  if (status === "finished") {
    return "Reviewed";
  }
  return "Incomplete";
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


function formatQueueEntityTotal(counts: EntityCounts): string | null {
  const total = ENTITY_COUNT_LABELS.reduce((sum, { key }) => sum + counts[key], 0);
  if (total === 0) {
    return null;
  }
  return total === 1 ? "1 entity" : `${total} entities`;
}

function countVisibleEntities(items: NormalizedEntity[]): number {
  return items.filter((item) => !item.hidden).length;
}

function entityGroupItems(entities: EntityGroups, group: EditableEntityGroup): NormalizedEntity[] {
  return entities.groups.find((entry) => entry.group === group)?.items ?? [];
}

function isRejectedEntity(item: NormalizedEntity): boolean {
  return item.hidden;
}

function countRejectedEntities(entities: EntityGroups): number {
  return entities.groups.reduce(
    (total, group) => total + group.items.filter((item) => isRejectedEntity(item)).length,
    0
  );
}

function tagsEqual(left: string[], right: string[]): boolean {
  return left.length === right.length && left.every((tag, index) => tag === right[index]);
}

function entityDraftError(draft: EntityEditDraft): string | null {
  if (!draft.title.trim()) {
    return "Title cannot be empty.";
  }
  if (draft.description !== "" && !draft.description.trim()) {
    return "Description cannot be empty.";
  }
  if (draft.tags.some((tag) => normalizeTagSlug(tag) === null)) {
    return draft.group === "tools"
      ? "Traits cannot be empty or contain commas."
      : "Tags cannot be empty or contain commas.";
  }
  if (draft.group === "tools" && draft.types.some((typeName) => normalizeTagSlug(typeName) === null)) {
    return "Tool kinds cannot be empty or contain commas.";
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
  types?: string[];
} {
  const payload: {
    group: EditableEntityGroup;
    index: number;
    title?: string;
    description?: string;
    tags?: string[];
    types?: string[];
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
  if (!original || !tagsEqual(draft.tags, original.tags)) {
    payload.tags = draft.tags.map((tag) => normalizeTagSlug(tag) ?? tag);
  }
  if (draft.group === "tools" && (!original || !tagsEqual(draft.types, original.types))) {
    payload.types = draft.types.map((typeName) => normalizeTagSlug(typeName) ?? typeName);
  }
  return payload;
}

function entityDraftUnchanged(draft: EntityEditDraft, item: NormalizedEntity): boolean {
  return (
    draft.title === item.title &&
    draft.description === item.description &&
    tagsEqual(draft.tags, item.tags) &&
    tagsEqual(draft.types, item.types)
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
      {queue.decision_counts.needs_attention} attention · {selectedCount} shown
    </p>
  );
}

function QueueStatusSummary({ counts }: { counts: QueueCounts }): ReactElement {
  return (
    <p className="queue-status-summary">
      {counts.total} total · {counts.in_progress} ready · {counts.pending} needs analysis ·{" "}
      {counts.finished} reviewed
    </p>
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
    <section className="source-header source-header-compact">
      <div className="source-header-content">
        <p className="eyebrow">{source.metadata.publication || source.metadata.category || "Source"}</p>
        <h2>{source.metadata.title}</h2>
        <p className="source-byline">
          {source.metadata.author || "Unknown author"} · {source.metadata.published_date || "No date"} ·{" "}
          {sourceReviewStatusLabel(source.status)}
        </p>
        <details className="source-meta-details">
          <summary>Source details</summary>
          <div className="status-row quiet-meta">
            {source.stale === null ? (
              <span>Sync unknown</span>
            ) : source.stale ? (
              <span>Out of date</span>
            ) : (
              <span>Up to date</span>
            )}
            <span>Readwise {source.metadata.readwise_id || "unknown"}</span>
          </div>
          <ManagementDecisionState review={source.management_review} />
        </details>
      </div>
      <div className="source-header-actions">
        <span className="queue-position">
          {selectedIndex >= 0 ? `${selectedIndex + 1} / ${visibleTotal}` : "No source"}
        </span>
        <div className="button-row nav-buttons">
          <button disabled={!canMovePrevious} onClick={onMovePrevious}>
            Previous
          </button>
          <button disabled={!canMoveNext} onClick={onMoveNext}>
            Next
          </button>
        </div>
        <button className="primary-action" disabled={finishPending || decisionPending} onClick={onFinish}>
          Finish as approved
        </button>
        <div className="decision-actions secondary-actions" aria-label="Article decisions">
          {DECISION_ACTIONS.map((action) => (
            <button
              className="secondary-action"
              disabled={decisionPending || finishPending}
              key={action.status}
              onClick={() => void onDecision(action.status)}
            >
              {action.label}
            </button>
          ))}
        </div>
        {finishMessage ? <p className="action-feedback success-message">{finishMessage}</p> : null}
        {finishError ? <p className="action-feedback error-message">{finishError}</p> : null}
        {decisionMessage ? <p className="action-feedback success-message">{decisionMessage}</p> : null}
        {decisionError ? <p className="action-feedback error-message">{decisionError}</p> : null}
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
    return <p className="management-review-state quiet">Not reviewed yet</p>;
  }
  return (
    <div className={`management-review-state quiet ${managementStatusClass(review.status)}`}>
      <strong>{managementStatusLabel(review.status)}</strong>
      <span>{review.reviewed_by}</span>
      <span>{review.reviewed_at}</span>
      {review.notes ? <p>{review.notes}</p> : null}
    </div>
  );
}

function ExtractionOverview({ entities }: { entities: EntityGroups }): ReactElement {
  const chips = entities.groups.map((group) => ({
    group: group.group,
    label: group.label,
    visibleCount: countVisibleEntities(group.items),
    totalCount: group.items.length
  }));
  return (
    <section className="extraction-overview" aria-label="Extraction overview">
      <h3>Extraction overview</h3>
      <div className="extraction-overview-grid">
        {chips.map((chip) => (
          <span
            className={
              chip.visibleCount === 0
                ? "extraction-chip extraction-chip-empty"
                : "extraction-chip"
            }
            key={chip.group}
          >
            {chip.label} {chip.visibleCount}
            {chip.totalCount > chip.visibleCount ? ` (${chip.totalCount - chip.visibleCount} rejected)` : ""}
          </span>
        ))}
      </div>
    </section>
  );
}

function SummaryCard({ source }: { source: SourceDetailResponse }): ReactElement {
  const easyRead = source.summary.short || "No easy read available.";
  const chapters = source.summary.chapters ?? [];
  const hasChapters = chapters.some(
    (chapter) => chapter.body.trim().length > 0 || chapter.items.length > 0
  );
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
      {hasChapters ? (
        <details className="source-summary-details">
          <summary>Full source summary</summary>
          <div className="source-summary-chapters">
            {chapters.map((chapter) => {
              const empty = !chapter.body.trim() && chapter.items.length === 0;
              return (
                <section className="source-summary-chapter" key={chapter.key}>
                  <h4>{chapter.label}</h4>
                  {empty ? <p className="quiet-empty">No content.</p> : null}
                  {chapter.items.length > 0 ? (
                    <ul>
                      {chapter.items.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  ) : null}
                  {chapter.items.length === 0 && chapter.body.trim() ? (
                    <p className="source-summary-body">{chapter.body}</p>
                  ) : null}
                </section>
              );
            })}
          </div>
        </details>
      ) : null}
    </section>
  );
}

function TagCloud({ tags }: { tags: string[] }): ReactElement {
  if (tags.length === 0) {
    return (
      <section className="review-section-quiet">
        <h3>Article tags</h3>
        <p className="quiet-empty">No article tags.</p>
      </section>
    );
  }
  return (
    <section className="review-section-quiet">
      <h3>Article tags</h3>
      <div className="tag-cloud quiet">
        {tags.map((tag) => (
          <span key={tag}>{tag}</span>
        ))}
      </div>
    </section>
  );
}

function EntitySections({
  availableTags,
  availableTypes,
  editDraft,
  entityError,
  entityMessage,
  entityMessageKey,
  entityPending,
  entities,
  onCancelEdit,
  onDraftChange,
  onReject,
  onRestore,
  onSaveEdit,
  onStartEdit,
  showRejected,
  onShowRejectedChange,
  tagsLoading,
  typesLoading
}: {
  availableTags: ReviewTagChoice[];
  availableTypes: ReviewTagChoice[];
  editDraft: EntityEditDraft | null;
  entityError: string | null;
  entityMessage: string | null;
  entityMessageKey: string | null;
  entityPending: boolean;
  entities: EntityGroups;
  onCancelEdit: () => void;
  onDraftChange: (draft: EntityEditDraft) => void;
  onReject: (group: EditableEntityGroup, index: number) => void;
  onRestore: (group: EditableEntityGroup, index: number) => void;
  onSaveEdit: () => void;
  onStartEdit: (group: EditableEntityGroup, item: NormalizedEntity) => void;
  showRejected: boolean;
  onShowRejectedChange: (showRejected: boolean) => void;
  tagsLoading: boolean;
  typesLoading: boolean;
}): ReactElement {
  const rejectedCount = countRejectedEntities(entities);
  return (
    <section className="entity-workspace">
      {rejectedCount > 0 ? (
        <label className="inline-toggle">
          <input
            checked={showRejected}
            onChange={(event) => onShowRejectedChange(event.target.checked)}
            type="checkbox"
          />
          Show rejected entities ({rejectedCount})
        </label>
      ) : null}
      {ENTITY_SECTIONS.map((section) => (
        <EntitySectionBlock
          availableTags={availableTags}
          availableTypes={availableTypes}
          editDraft={editDraft}
          entityError={entityError}
          entityMessage={entityMessage}
          entityMessageKey={entityMessageKey}
          entityPending={entityPending}
          groups={entities.groups.filter((group) => group.section === section.section)}
          key={section.section}
          onCancelEdit={onCancelEdit}
          onDraftChange={onDraftChange}
          onReject={onReject}
          onRestore={onRestore}
          onSaveEdit={onSaveEdit}
          onStartEdit={onStartEdit}
          sectionTitle={section.title}
          showRejected={showRejected}
          tagsLoading={tagsLoading}
          typesLoading={typesLoading}
        />
      ))}
    </section>
  );
}

function EntitySectionBlock({
  availableTags,
  availableTypes,
  editDraft,
  entityError,
  entityMessage,
  entityMessageKey,
  entityPending,
  groups,
  onCancelEdit,
  onDraftChange,
  onReject,
  onRestore,
  onSaveEdit,
  onStartEdit,
  sectionTitle,
  showRejected,
  tagsLoading,
  typesLoading
}: {
  availableTags: ReviewTagChoice[];
  availableTypes: ReviewTagChoice[];
  editDraft: EntityEditDraft | null;
  entityError: string | null;
  entityMessage: string | null;
  entityMessageKey: string | null;
  entityPending: boolean;
  groups: NormalizedEntityGroup[];
  onCancelEdit: () => void;
  onDraftChange: (draft: EntityEditDraft) => void;
  onReject: (group: EditableEntityGroup, index: number) => void;
  onRestore: (group: EditableEntityGroup, index: number) => void;
  onSaveEdit: () => void;
  onStartEdit: (group: EditableEntityGroup, item: NormalizedEntity) => void;
  sectionTitle: string;
  showRejected: boolean;
  tagsLoading: boolean;
  typesLoading: boolean;
}): ReactElement | null {
  const visibleGroups = groups.filter((group) => {
    const visibleItems = showRejected
      ? group.items
      : group.items.filter((item) => !isRejectedEntity(item));
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
            availableTags={availableTags}
            availableTypes={availableTypes}
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
            onReject={onReject}
            onRestore={onRestore}
            onSaveEdit={onSaveEdit}
            onStartEdit={onStartEdit}
            showRejected={showRejected}
            tagsLoading={tagsLoading}
            title={group.label}
            typesLoading={typesLoading}
          />
        ))}
      </div>
    </section>
  );
}

function EntityGroup({
  availableTags,
  availableTypes,
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
  onReject,
  onRestore,
  onSaveEdit,
  onStartEdit,
  showRejected,
  tagsLoading,
  typesLoading
}: {
  availableTags: ReviewTagChoice[];
  availableTypes: ReviewTagChoice[];
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
  onReject: (group: EditableEntityGroup, index: number) => void;
  onRestore: (group: EditableEntityGroup, index: number) => void;
  onSaveEdit: () => void;
  onStartEdit: (group: EditableEntityGroup, item: NormalizedEntity) => void;
  showRejected: boolean;
  tagsLoading: boolean;
  typesLoading: boolean;
}): ReactElement {
  const visibleItems = showRejected ? items : items.filter((item) => !isRejectedEntity(item));
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
            availableTags={availableTags}
            availableTypes={availableTypes}
            editDraft={isEditing ? editDraft : null}
            entityError={isEditing ? entityError : null}
            entityMessage={entityKey(group, item.index) === entityMessageKey ? entityMessage : null}
            entityPending={entityPending}
            group={group}
            item={item}
            key={`${title}-${item.index}-${item.title}`}
            onCancelEdit={onCancelEdit}
            onDraftChange={onDraftChange}
            onReject={onReject}
            onRestore={onRestore}
            onSaveEdit={onSaveEdit}
            onShowRejected={showRejected}
            onStartEdit={onStartEdit}
            tagsLoading={tagsLoading}
            typesLoading={typesLoading}
          />
        );
      })}
    </section>
  );
}

function EntityCard({
  availableTags,
  availableTypes,
  editDraft,
  entityError,
  entityMessage,
  entityPending,
  group,
  item,
  onCancelEdit,
  onDraftChange,
  onReject,
  onRestore,
  onSaveEdit,
  onShowRejected,
  onStartEdit,
  tagsLoading,
  typesLoading
}: {
  availableTags: ReviewTagChoice[];
  availableTypes: ReviewTagChoice[];
  editDraft: EntityEditDraft | null;
  entityError: string | null;
  entityMessage: string | null;
  entityPending: boolean;
  group: EditableEntityGroup;
  item: NormalizedEntity;
  onCancelEdit: () => void;
  onDraftChange: (draft: EntityEditDraft) => void;
  onReject: (group: EditableEntityGroup, index: number) => void;
  onRestore: (group: EditableEntityGroup, index: number) => void;
  onSaveEdit: () => void;
  onShowRejected: boolean;
  onStartEdit: (group: EditableEntityGroup, item: NormalizedEntity) => void;
  tagsLoading: boolean;
  typesLoading: boolean;
}): ReactElement {
  const entityTitle = item.title || "Untitled entity";
  const rejected = isRejectedEntity(item);
  if (editDraft) {
    const validationError = entityDraftError(editDraft);
    const unchanged = entityDraftUnchanged(editDraft, item);
    const isTool = editDraft.group === "tools";
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
        {isTool ? (
          <TagPicker
            availableTags={availableTypes}
            createLabelPrefix="Create new kind"
            disabled={entityPending}
            emptyLabel="No tool kind selected"
            helperText="What kind of product?"
            label="Tool kind"
            loading={typesLoading}
            newTags={editDraft.newTypeNames}
            onChange={(types, newTypeNames) =>
              onDraftChange({ ...editDraft, types, newTypeNames })
            }
            placeholder="Search tool kinds"
            searchAriaLabel="Search or create tool kinds"
            tags={editDraft.types}
          />
        ) : null}
        <TagPicker
          availableTags={availableTags}
          createLabelPrefix={isTool ? "Create new trait" : "Create new tag"}
          disabled={entityPending}
          emptyLabel={isTool ? "No traits selected" : "No tags selected"}
          helperText={isTool ? "How it's used or deployed" : undefined}
          label={isTool ? "Traits" : "Entity tags"}
          loading={tagsLoading}
          newTags={editDraft.newTagNames}
          onChange={(tags, newTagNames) => onDraftChange({ ...editDraft, tags, newTagNames })}
          placeholder={isTool ? "Search traits" : "Search tags"}
          searchAriaLabel={isTool ? "Search or create traits" : "Search or create tags"}
          tags={editDraft.tags}
        />
        {unchanged ? (
          <p className="helper-text">
            {isTool
              ? "Change title, description, tool kind, or traits to save."
              : "Change title, description, or tags to save."}
          </p>
        ) : null}
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
  const isTool = group === "tools";
  return (
    <article className={rejected ? "entity-card rejected-entity" : "entity-card"}>
      <div className="entity-card-header">
        <h4>{entityTitle}</h4>
        <div className="entity-card-actions">
          <button
            aria-label={`Edit ${entityTitle}`}
            disabled={entityPending}
            onClick={() => onStartEdit(group, item)}
          >
            Edit
          </button>
          {rejected ? (
            onShowRejected ? (
              <button
                aria-label={`Restore ${entityTitle}`}
                disabled={entityPending}
                onClick={() => onRestore(group, item.index)}
              >
                Restore
              </button>
            ) : null
          ) : (
            <button
              aria-label={`Reject ${entityTitle}`}
              disabled={entityPending}
              onClick={() => onReject(group, item.index)}
            >
              Reject
            </button>
          )}
        </div>
      </div>
      {rejected ? <span className="rejected-badge">Rejected</span> : null}
      {isTool && item.types.length > 0 ? (
        <div className="entity-meta-block entity-card-kinds">
          <div className="entity-meta-heading">
            <span className="entity-meta-label">Tool kind</span>
            <span className="entity-meta-helper">What kind of product?</span>
          </div>
          <div className="tag-cloud compact">
            {item.types.map((typeName) => (
              <span className="type-chip" key={typeName}>
                {typeName}
              </span>
            ))}
          </div>
        </div>
      ) : null}
      {isTool && item.tags.length > 0 ? (
        <div className="entity-meta-block entity-card-traits">
          <div className="entity-meta-heading">
            <span className="entity-meta-label">Traits</span>
            <span className="entity-meta-helper">How it's used or deployed</span>
          </div>
          <div className="tag-cloud compact">
            {item.tags.map((tag) => (
              <span key={tag}>{tag}</span>
            ))}
          </div>
        </div>
      ) : null}
      {!isTool && item.tags.length > 0 ? (
        <div className="tag-cloud compact entity-card-tags">
          {item.tags.map((tag) => (
            <span key={tag}>{tag}</span>
          ))}
        </div>
      ) : null}
      {item.description ? <p className="entity-description">{item.description}</p> : null}
      {entityMessage ? <p className="success-message inline">{entityMessage}</p> : null}
      {!isTool && item.types.length > 0 ? (
        <div className="tag-cloud compact entity-card-types">
          {item.types.map((typeName) => (
            <span className="type-chip" key={typeName}>
              {typeName}
            </span>
          ))}
        </div>
      ) : null}
      <EntityFullExtraction item={item} />
    </article>
  );
}

function EntityFullExtraction({ item }: { item: NormalizedEntity }): ReactElement {
  const scalars = [...(item.detail_scalars ?? [])];
  const lists = [...(item.detail_lists ?? [])];
  if (scalars.length === 0 && item.description.trim()) {
    scalars.push({ label: "Summary", body: item.description });
  }
  if (
    item.evidence.trim() &&
    !scalars.some((field) => field.body.trim() === item.evidence.trim())
  ) {
    scalars.push({ label: "Evidence", body: item.evidence });
  }
  const fieldCount = scalars.length + lists.length;
  return (
    <details className="entity-full-extraction">
      <summary>Full extraction{fieldCount > 0 ? ` (${fieldCount})` : ""}</summary>
      <div className="entity-full-extraction-body">
        {fieldCount === 0 ? <p className="quiet-empty">No extraction fields available.</p> : null}
        {scalars.map((field) => (
          <section className="entity-full-field" key={field.label}>
            <h5>{field.label}</h5>
            <p>{field.body}</p>
          </section>
        ))}
        {lists.map((detailList) => (
          <section className="entity-full-field" key={detailList.label}>
            <h5>
              {detailList.label} ({detailList.items.length})
            </h5>
            <ul>
              {detailList.items.map((entry) => (
                <li key={entry}>{entry}</li>
              ))}
            </ul>
          </section>
        ))}
      </div>
    </details>
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
