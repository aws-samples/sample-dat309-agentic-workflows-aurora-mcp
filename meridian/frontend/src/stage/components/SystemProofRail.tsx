/**
 * SystemProofRail — right rail with Aurora schema, MCP tool catalog, and
 * governance gates. Each card highlights when the relevant span is active.
 */
import type { StageScenario, StageSpan, StageSystemId } from '../types';

const AURORA_TABLES = [
  { name: 'trip_packages', kind: 'data + vector' },
  { name: 'traveler_preferences', kind: 'memory + RLS' },
  { name: 'trip_interactions', kind: 'history' },
  { name: 'conversations', kind: 'memory' },
  { name: 'bookings', kind: 'holds' },
  { name: 'agent_traces', kind: 'observability' },
];

const MCP_TOOLS: { name: string; meta: string }[] = [
  { name: 'postgres.run_query', meta: 'typed SQL' },
  { name: 'trips.hybrid_search', meta: 'pgvector + ts' },
  { name: 'memory.recall', meta: 'Aurora · RLS' },
  { name: 'availability.lookup', meta: 'inventory' },
  { name: 'bookings.hold', meta: 'governed' },
  { name: 'claude.compose', meta: 'Bedrock' },
];

interface SystemProofRailProps {
  scenario: StageScenario;
  activeSpan: StageSpan | null;
  activeSystem: StageSystemId | null;
}

function ShieldIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path d="M8 1.5L13.5 3.5V8C13.5 11.3137 11.0376 13.7461 8 14.5C4.9624 13.7461 2.5 11.3137 2.5 8V3.5L8 1.5Z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
      <path d="M5.5 8.2L7.2 9.9L10.5 6.6" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function SystemProofRail({ scenario, activeSpan, activeSystem }: SystemProofRailProps) {
  const calledTools = new Set(
    scenario.spans
      .filter((s) => s.kind === 'tool' || s.kind === 'model')
      .map((s) => s.name.toLowerCase()),
  );
  const callingToolName = activeSpan?.kind === 'tool' || activeSpan?.kind === 'model'
    ? activeSpan.name.toLowerCase()
    : null;

  const touchedTables = new Set<string>();
  if (activeSpan?.kind === 'memory') touchedTables.add('traveler_preferences');
  if (activeSpan?.kind === 'data' || activeSpan?.kind === 'tool') {
    touchedTables.add('trip_packages');
    touchedTables.add('bookings');
  }
  if (activeSpan?.kind === 'synthesis') touchedTables.add('agent_traces');

  return (
    <aside className="ds-rail" aria-label="System proof">
      <section
        className={`ds-rail-card${activeSystem === 'aurora' || activeSystem === 'memory' ? ' is-active' : ''}`}
        data-system={activeSystem === 'memory' ? 'memory' : 'aurora'}
        aria-label="Aurora spine"
      >
        <header className="ds-rail-card-head">
          <div className="ds-rail-card-title">Aurora spine</div>
          <div className="ds-rail-card-sub">tables touched</div>
        </header>
        <div className="ds-aurora-spine">
          {AURORA_TABLES.map((t) => (
            <div
              key={t.name}
              className={`ds-aurora-table${touchedTables.has(t.name) ? ' is-touched' : ''}`}
            >
              <span>{t.name}</span>
              <span>{t.kind}</span>
            </div>
          ))}
        </div>
      </section>

      <section
        className={`ds-rail-card${activeSystem === 'mcp' || activeSystem === 'model' ? ' is-active' : ''}`}
        data-system="mcp"
        aria-label="MCP tool catalog"
      >
        <header className="ds-rail-card-head">
          <div className="ds-rail-card-title">MCP tools</div>
          <div className="ds-rail-card-sub">6 typed</div>
        </header>
        <div>
          {MCP_TOOLS.map((tool) => {
            const calling = callingToolName != null && tool.name.toLowerCase() === callingToolName;
            const wasCalled = calledTools.has(tool.name.toLowerCase());
            return (
              <div
                key={tool.name}
                className={`ds-mcp-tool${calling ? ' is-called' : wasCalled ? ' is-called' : ''}`}
              >
                <span>{tool.name}</span>
                <span>{tool.meta}</span>
              </div>
            );
          })}
        </div>
      </section>

      <section
        className={`ds-rail-card${activeSystem === 'governance' ? ' is-active' : ''}`}
        data-system="governance"
        aria-label="Governance"
      >
        <header className="ds-rail-card-head">
          <div className="ds-rail-card-title">Governance</div>
          <div className="ds-rail-card-sub">policy gates</div>
        </header>
        <div className="ds-gov">
          <div className="ds-gov-row">
            <ShieldIcon />
            <div>
              <b>{scenario.governance.scope}</b>
              <span>agent scope</span>
            </div>
          </div>
          <div className="ds-gov-row">
            <ShieldIcon />
            <div>
              <b>{scenario.governance.budgetCap}</b>
              <span>budget cap</span>
            </div>
          </div>
          <div className="ds-gov-row">
            <ShieldIcon />
            <div>
              <b>{scenario.governance.confirmation}</b>
              <span>human-in-the-loop</span>
            </div>
          </div>
          <div className="ds-gov-row">
            <ShieldIcon />
            <div>
              <b>{scenario.governance.audit}</b>
              <span>agent_traces · INSERT</span>
            </div>
          </div>
        </div>
      </section>
    </aside>
  );
}
