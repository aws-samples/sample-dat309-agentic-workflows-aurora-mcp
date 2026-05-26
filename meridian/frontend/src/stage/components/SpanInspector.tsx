/**
 * SpanInspector — drawer that opens when an audience-level trace row is
 * clicked. Shows input, output, latency, cost, SQL/tool/model, and related
 * Aurora table.
 */
import { useEffect } from 'react';
import type { StageSpan } from '../types';

interface SpanInspectorProps {
  span: StageSpan | null;
  onClose: () => void;
}

function relatedTableForSpan(span: StageSpan): string | null {
  if (span.kind === 'memory') return 'traveler_preferences';
  if (span.kind === 'data') return 'trip_packages · bookings';
  if (span.kind === 'tool') return span.source ?? 'mcp.tools';
  if (span.kind === 'synthesis') return 'agent_traces';
  if (span.kind === 'security') return 'agent_audit_log';
  if (span.kind === 'model') return 'bedrock.model';
  return null;
}

export function SpanInspector({ span, onClose }: SpanInspectorProps) {
  // Esc-to-close. Kiosk callers can just not mount the inspector; this hook
  // is only active while one is open.
  useEffect(() => {
    if (!span) return;
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose();
    }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [span, onClose]);

  if (!span) return null;

  const related = relatedTableForSpan(span);

  return (
    <div className="ds-inspector-backdrop" onClick={onClose} role="presentation">
      <aside
        className="ds-inspector"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label={`Span detail: ${span.name}`}
      >
        <header className="ds-inspector-head">
          <div>
            <div className="ds-inspector-title">{span.name}</div>
            <div className="ds-inspector-sub">
              {span.component ?? span.source ?? span.kind} · {span.latencyMs}ms
            </div>
          </div>
          <button type="button" className="ds-inspector-close" onClick={onClose} aria-label="Close inspector">×</button>
        </header>

        <div className="ds-inspector-body">
          <div className="ds-inspector-meta">
            <div>
              <span>Latency</span>
              <b>{span.latencyMs}ms</b>
            </div>
            <div>
              <span>Status</span>
              <b>{span.status ?? 'ok'}</b>
            </div>
            <div>
              <span>Cost</span>
              <b>{span.costUsd != null ? `$${span.costUsd.toFixed(3)}` : '—'}</b>
            </div>
            <div>
              <span>Tokens</span>
              <b>
                {span.tokensIn != null || span.tokensOut != null
                  ? `${span.tokensIn ?? '—'} / ${span.tokensOut ?? '—'}`
                  : '—'}
              </b>
            </div>
          </div>

          <div className="ds-inspector-section">
            <h4>Input</h4>
            <pre className="ds-inspector-code">{span.input ?? '—'}</pre>
          </div>

          <div className="ds-inspector-section">
            <h4>Output</h4>
            <pre className="ds-inspector-code">{span.output ?? '—'}</pre>
          </div>

          <div className="ds-inspector-section">
            <h4>Source</h4>
            <pre className="ds-inspector-code">{span.source ?? span.component ?? '—'}</pre>
          </div>

          {related && (
            <div className="ds-inspector-section">
              <h4>Related</h4>
              <pre className="ds-inspector-code">{related}</pre>
            </div>
          )}
        </div>
      </aside>
    </div>
  );
}
