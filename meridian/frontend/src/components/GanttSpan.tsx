/**
 * GanttSpan — Meridian Pro Gantt-style trace row.
 *
 * Maps the existing ActivityEntry telemetry to a horizontal time bar.
 */
import type { ActivityEntry } from '../types';

const TAG_LABEL: Record<string, string> = {
  runtime: 'Runtime',
  memory_short: 'Short memory',
  memory_long: 'Long memory',
  orchestration: 'Orchestration',
  model: 'Model',
  tool: 'Tool · MCP',
  data: 'Data',
  synthesis: 'Synthesis',
};

interface GanttSpanProps {
  entry: ActivityEntry;
  index: number;
  totalSpans: number;
  state: 'done' | 'live' | 'pending';
}

export function GanttSpan({ entry, index, totalSpans, state }: GanttSpanProps) {
  const category = entry.telemetry?.category ?? 'runtime';
  const label = TAG_LABEL[category] ?? 'Step';

  // Compute a simple proportional bar so the timeline reads like a Gantt
  // (we don't have real start offsets in the API today, so we lay out by index).
  const barWidthPct = Math.max(8, 100 / Math.max(totalSpans, 1));
  const leftPct = (index / Math.max(totalSpans, 1)) * (100 - barWidthPct);

  return (
    <div className={`mp-gspan ${state}`}>
      <div className="mp-gspan-row">
        <div style={{ minWidth: 0 }}>
          <span className={`mp-gspan-tag mp-tag-${category}`}>{label}</span>
          <div className="mp-gspan-name">
            {entry.title}
            {entry.agent_name && <small>{entry.agent_name}{entry.agent_file ? ` · ${entry.agent_file}` : ''}</small>}
          </div>
        </div>
        <div className="mp-gspan-time">
          {state === 'live'
            ? `${entry.execution_time_ms ?? '…'}ms · live`
            : entry.execution_time_ms != null
              ? `${entry.execution_time_ms}ms`
              : '—'}
        </div>
      </div>
      <div className="mp-gspan-bar">
        <span style={{ left: `${leftPct}%`, width: `${barWidthPct}%` }} />
      </div>
      {entry.details && (
        <div className="mp-gspan-detail">{entry.details}</div>
      )}
      {entry.sql_query && (
        <pre className="mp-gspan-sql">{entry.sql_query}</pre>
      )}
    </div>
  );
}
