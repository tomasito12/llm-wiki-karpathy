import { useEffect, useMemo, useState } from "react";
import type { ReactElement } from "react";

import { getConfig, getRawSource, getReviewQueue, getSourceDetail } from "./api";
import "./styles.css";
import type {
  ConfigResponse,
  EntityGroups,
  NormalizedEntity,
  QueueResponse,
  QueueStatusFilter,
  RawSourceResponse,
  SourceDetailResponse
} from "./types";

const STATUS_OPTIONS: Array<{ value: QueueStatusFilter; label: string }> = [
  { value: "all", label: "All" },
  { value: "pending", label: "Pending" },
  { value: "in_progress", label: "In progress" },
  { value: "finished", label: "Finished" },
  { value: "incomplete", label: "Incomplete" }
];

export default function App(): ReactElement {
  const [config, setConfig] = useState<ConfigResponse | null>(null);
  const [queue, setQueue] = useState<QueueResponse | null>(null);
  const [source, setSource] = useState<SourceDetailResponse | null>(null);
  const [rawSource, setRawSource] = useState<RawSourceResponse | null>(null);
  const [selectedSourceId, setSelectedSourceId] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<QueueStatusFilter>("all");
  const [query, setQuery] = useState("");
  const [rawOpen, setRawOpen] = useState(false);
  const [debugOpen, setDebugOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getConfig().then(setConfig).catch((err: unknown) => setError(String(err)));
  }, []);

  useEffect(() => {
    getReviewQueue({ status: statusFilter, q: query })
      .then((payload) => {
        setQueue(payload);
        setSelectedSourceId((current) => {
          if (current && payload.items.some((item) => item.source_id === current)) {
            return current;
          }
          return payload.items[0]?.source_id ?? null;
        });
      })
      .catch((err: unknown) => setError(String(err)));
  }, [query, statusFilter]);

  useEffect(() => {
    if (!selectedSourceId) {
      setSource(null);
      return;
    }
    setRawOpen(false);
    setDebugOpen(false);
    setRawSource(null);
    getSourceDetail(selectedSourceId).then(setSource).catch((err: unknown) => setError(String(err)));
  }, [selectedSourceId]);

  const selectedIndex = useMemo(() => {
    if (!queue || !selectedSourceId) {
      return -1;
    }
    return queue.items.findIndex((item) => item.source_id === selectedSourceId);
  }, [queue, selectedSourceId]);

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

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <h1>Management Web</h1>
          <p>Fast batch review for pre-analyzed Readwise sources</p>
        </div>
        <div className="mode-pill">Read-only</div>
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
                  {item.status.replace("_", " ")} · {item.entity_counts.topics} topics
                </small>
              </button>
            ))}
            {queue?.items.length === 0 ? <p className="empty-state">No sources match.</p> : null}
          </section>
        </aside>

        <section className="review-panel">
          {source ? (
            <>
              <SourceHeader source={source} />
              <SummaryCard source={source} />
              <TagCloud tags={source.tags} />
              <EntitySections entities={source.entities} />
              <div className="drawer-actions">
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
        </section>

        <aside className="side-panel">
          <section className="panel-card">
            <h2>Position</h2>
            <p>
              {selectedIndex >= 0 && queue
                ? `${selectedIndex + 1} of ${queue.items.length}`
                : "No source selected"}
            </p>
            <div className="button-row">
              <button disabled={selectedIndex <= 0} onClick={() => moveSelection(-1)}>
                Previous
              </button>
              <button
                disabled={!queue || selectedIndex < 0 || selectedIndex >= queue.items.length - 1}
                onClick={() => moveSelection(1)}
              >
                Next
              </button>
            </div>
          </section>

          <section className="panel-card">
            <h2>Article Actions</h2>
            <p className="readonly-note">Read-only slice: these controls are placeholders.</p>
            <button disabled>Approve article</button>
            <button disabled>Needs attention</button>
            <button disabled>Skip</button>
            <button disabled>Request re-analysis</button>
          </section>

          <section className="panel-card path-card">
            <h2>Paths</h2>
            <p>{config?.paths.raw_dir ?? "Loading raw path..."}</p>
            <p>{config?.paths.reviews_dir ?? "Loading reviews path..."}</p>
          </section>
        </aside>
      </main>
    </div>
  );
}

function QueueCountsCard({ queue }: { queue: QueueResponse | null }): ReactElement {
  return (
    <section className="counts-grid">
      <Metric label="Total" value={queue?.counts.total ?? 0} />
      <Metric label="Pending" value={queue?.counts.pending ?? 0} />
      <Metric label="In progress" value={queue?.counts.in_progress ?? 0} />
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

function SourceHeader({ source }: { source: SourceDetailResponse }): ReactElement {
  return (
    <section className="source-header">
      <div>
        <p className="eyebrow">{source.metadata.publication || source.metadata.category || "Source"}</p>
        <h2>{source.metadata.title}</h2>
        <p>
          {source.metadata.author || "Unknown author"} · {source.metadata.published_date || "No date"}
        </p>
      </div>
      <div className="status-stack">
        <span>{source.status.replace("_", " ")}</span>
        <span>{source.stale === null ? "Stale unknown" : source.stale ? "Stale" : "Current"}</span>
        <span>Readwise {source.metadata.readwise_id || "unknown"}</span>
      </div>
    </section>
  );
}

function SummaryCard({ source }: { source: SourceDetailResponse }): ReactElement {
  return (
    <section className="review-card">
      <h3>Summary</h3>
      <p>{source.summary.short || "No source summary available."}</p>
      {source.summary.key_insights.length > 0 ? (
        <ul>
          {source.summary.key_insights.map((insight) => (
            <li key={insight}>{insight}</li>
          ))}
        </ul>
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

function EntitySections({ entities }: { entities: EntityGroups }): ReactElement {
  return (
    <div className="entity-grid">
      <EntityGroup title="Topics" items={entities.topics} />
      <EntityGroup title="Glossary" items={entities.glossary} />
      <EntityGroup title="Trends" items={entities.trends} />
    </div>
  );
}

function EntityGroup({
  title,
  items
}: {
  title: string;
  items: NormalizedEntity[];
}): ReactElement {
  return (
    <section className="review-card entity-group">
      <h3>
        {title} <span>{items.length}</span>
      </h3>
      {items.length > 0 ? (
        items.map((item) => <EntityCard key={`${title}-${item.title}`} item={item} />)
      ) : (
        <p className="empty-state">No {title.toLowerCase()} extracted.</p>
      )}
    </section>
  );
}

function EntityCard({ item }: { item: NormalizedEntity }): ReactElement {
  return (
    <article className="entity-card">
      <h4>{item.title || "Untitled entity"}</h4>
      {item.description ? <p>{item.description}</p> : null}
      {item.tags.length > 0 ? (
        <div className="tag-cloud compact">
          {item.tags.map((tag) => (
            <span key={tag}>{tag}</span>
          ))}
        </div>
      ) : null}
      {item.evidence ? <blockquote>{item.evidence}</blockquote> : null}
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
