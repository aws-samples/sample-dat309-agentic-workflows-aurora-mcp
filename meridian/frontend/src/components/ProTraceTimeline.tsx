/**
 * ProTraceTimeline — kiosk-style horizontal trace rows for Meridian Pro (light).
 */
import type { ActivityEntry } from '../types';
import type { StageSpan } from '../stage/types';

const KIND_LABEL: Record<string, string> = {
  orchestration: 'orch',
  memory: 'memory',
  tool: 'mcp',
  data: 'aurora',
  model: 'model',
  synthesis: 'compose',
  security: 'policy',
};

interface ProTraceTimelineProps {
  spans: StageSpan[];
  activities: ActivityEntry[];
  activeIndex: number;
  selectedIndex: number | null;
  onSelect: (idx: number | null) => void;
  totalLatencyMs: number;
}

export function ProTraceTimeline({
  spans,
  activities,
  activeIndex,
  selectedIndex,
  onSelect,
  totalLatencyMs,
}: ProTraceTimelineProps) {
  const peak = Math.max(...spans.map((s) => s.latencyMs ?? 0), 1);

  if (!spans.length) {
    return (
      <div className="mp-trace-empty">
        <div className="pulser">
          <span /><span /><span />
        </div>
        <div>Waiting for activity</div>
        <div className="hint">Send a query — the trace produces the reply below</div>
      </div>
    );
  }

  return (
    <div className="mp-trace-hero">
      <div className="mp-trace-hero-stats">
        <div><span>Spans</span><b>{spans.length}</b></div>
        <div><span>Latency</span><b>{totalLatencyMs}ms</b></div>
        <div>
          <span>Active</span>
          <b>{activeIndex < 0 ? '—' : `${activeIndex + 1}/${spans.length}`}</b>
        </div>
      </div>

      <div className="mp-trace-canvas" role="list">
        {spans.map((span, idx) => {
          const widthPct = Math.max(8, Math.round(((span.latencyMs ?? 0) / peak) * 100));
          const isActive = idx === activeIndex;
          const isPending = activeIndex >= 0 && idx > activeIndex;
          const isSelected = selectedIndex === idx;
          const act = activities[idx];

          return (
            <div key={span.id} className="mp-trace-row-wrap">
              <button
                type="button"
                className={`mp-trace-row kind-${span.kind}${isActive ? ' is-active' : ''}${isPending ? ' is-pending' : ''}${isSelected ? ' is-selected' : ''}`}
                role="listitem"
                aria-pressed={isSelected}
                onClick={() => onSelect(isSelected ? null : idx)}
              >
                <span className="mp-trace-tag">{KIND_LABEL[span.kind] ?? span.kind}</span>
                <div className="mp-trace-meta">
                  <span className="mp-trace-name">{span.name}</span>
                  <span className="mp-trace-detail">
                    {span.component ?? span.detail ?? span.source ?? ''}
                  </span>
                </div>
                <div className="mp-trace-bar-cell">
                  <div className="mp-trace-bar" aria-hidden="true">
                    <span style={{ width: isPending ? '0%' : `${widthPct}%` }} />
                  </div>
                </div>
                <span className="mp-trace-ms">{span.latencyMs}ms</span>
              </button>
              {isSelected && act && (act.details || act.sql_query) && (
                <div className="mp-trace-inspector">
                  {act.details && <p>{act.details}</p>}
                  {act.sql_query && <pre>{act.sql_query}</pre>}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
