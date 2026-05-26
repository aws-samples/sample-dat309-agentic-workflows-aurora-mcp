/**
 * TraceHero — the dominant element on the Demo Stage.
 *
 * Renders the span timeline as a stack of animated horizontal bars. Each row
 * shows kind tag, name + detail, latency bar, ms. Rows are clickable buttons
 * that surface the inspector drawer.
 */
import { ConciergeResponseCard } from './ConciergeResponseCard';
import type { StageRecommendation, StageSpan } from '../types';

const KIND_LABEL: Record<string, string> = {
  orchestration: 'orch',
  memory: 'memory',
  tool: 'mcp tool',
  data: 'aurora',
  model: 'model',
  synthesis: 'compose',
  security: 'policy',
};

interface TraceHeroProps {
  spans: StageSpan[];
  activeIndex: number;
  selectedIndex: number | null;
  totalLatencyMs: number;
  onSelect: (idx: number) => void;
  view: 'audience' | 'builder';
  /** Natural-language reply rendered in the footer of the panel. */
  assistantReply: string;
  /** One-line provenance summary (e.g. "supervisor.plan → memory.recall → …"). */
  reasoning: string;
  /** Reveal state for the response card. */
  replyPhase: 'pending' | 'composing' | 'composed';
  /** Top recommendation, surfaced under the reply once composed. */
  primaryRecommendation?: StageRecommendation | null;
}

export function TraceHero({
  spans,
  activeIndex,
  selectedIndex,
  totalLatencyMs,
  onSelect,
  view,
  assistantReply,
  reasoning,
  replyPhase,
  primaryRecommendation,
}: TraceHeroProps) {
  const peak = Math.max(...spans.map((s) => s.latencyMs ?? 0), 1);

  return (
    <section className="ds-panel ds-trace-hero" aria-label="Agent trace">
      <header className="ds-trace-hero-header">
        <div className="ds-trace-hero-title">
          <span className="ds-trace-hero-eyebrow">The trip you describe</span>
          <h1 className="ds-trace-hero-heading">
            The trace that <em>proves it</em>.
          </h1>
        </div>
        <div className="ds-trace-stats">
          <div>
            Spans
            <b>{spans.length}</b>
          </div>
          <div>
            Latency
            <b>{totalLatencyMs}ms</b>
          </div>
          <div>
            Active
            <b>{activeIndex < 0 ? '—' : `${activeIndex + 1}/${spans.length}`}</b>
          </div>
        </div>
      </header>

      <div className="ds-trace-canvas" role="list">
        {spans.map((span, idx) => {
          const widthPct = Math.max(8, Math.round(((span.latencyMs ?? 0) / peak) * 100));
          const isActive = idx === activeIndex;
          const isPending = activeIndex >= 0 && idx > activeIndex;
          const isSelected = selectedIndex === idx;
          return (
            <button
              key={span.id}
              type="button"
              className={`ds-trace-row kind-${span.kind}${isActive ? ' is-active' : ''}${isPending ? ' is-pending' : ''}${isSelected ? ' is-selected' : ''}`}
              role="listitem"
              aria-label={`${span.name} ${span.latencyMs} milliseconds`}
              aria-pressed={isSelected}
              onClick={() => onSelect(idx)}
            >
              <span className="ds-trace-tag">{KIND_LABEL[span.kind] ?? span.kind}</span>
              <div className="ds-trace-meta">
                <span className="ds-trace-name">{span.name}</span>
                <span className="ds-trace-detail">
                  {view === 'builder' ? span.source ?? span.detail ?? span.component ?? '' : span.detail ?? span.component ?? ''}
                </span>
              </div>
              <div className="ds-trace-bar-cell">
                <div className="ds-trace-bar" aria-hidden="true">
                  <span style={{ width: isPending ? '0%' : `${widthPct}%` }} />
                </div>
              </div>
              <span className="ds-trace-ms">{span.latencyMs}ms</span>
            </button>
          );
        })}
      </div>

      <ConciergeResponseCard
        reply={assistantReply}
        reasoning={reasoning}
        phase={replyPhase}
        primary={primaryRecommendation ?? null}
      />
    </section>
  );
}
