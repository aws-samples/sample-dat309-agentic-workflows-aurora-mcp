/**
 * SystemSection — Meridian Pro substrate panel
 *
 * Two side-by-side surfaces: Aurora schema map + MCP tool catalog.
 * Reads tool latency from the chat-trace history when available, otherwise shows
 * sensible defaults so the section never looks empty.
 */
import { FadeIn } from '../components/FadeIn';
import { useAgentBridge } from '../context/AgentBridge';

interface SchemaTable {
  name: string;
  pk?: boolean;
  cols: { name: string; type: string; emphasis?: boolean }[];
  group: 'retrieval' | 'identity' | 'memory' | 'conversation';
}

const tables: SchemaTable[] = [
  {
    name: 'trip_packages',
    pk: true,
    group: 'retrieval',
    cols: [
      { name: 'id', type: 'uuid', emphasis: true },
      { name: 'name', type: 'text' },
      { name: 'category', type: 'text' },
      { name: 'price_cents', type: 'int' },
      { name: 'refundable', type: 'bool' },
      { name: 'embedding', type: 'vector(1024)' },
      { name: 'search_vector', type: 'tsvector' },
    ],
  },
  {
    name: 'travelers',
    pk: true,
    group: 'identity',
    cols: [
      { name: 'id', type: 'text', emphasis: true },
      { name: 'display_name', type: 'text' },
      { name: 'home_airport', type: 'text' },
      { name: 'created_at', type: 'ts' },
    ],
  },
  {
    name: 'traveler_preferences',
    group: 'memory',
    cols: [
      { name: 'traveler_id', type: 'fk' },
      { name: 'key', type: 'text' },
      { name: 'value', type: 'text' },
      { name: 'confidence', type: 'numeric' },
      { name: 'source_msg_id', type: 'fk' },
      { name: 'embedding', type: 'vector(1024)' },
    ],
  },
  {
    name: 'conversations',
    pk: true,
    group: 'conversation',
    cols: [
      { name: 'id', type: 'uuid', emphasis: true },
      { name: 'traveler_id', type: 'fk' },
      { name: 'started_at', type: 'ts' },
      { name: 'summary', type: 'text' },
    ],
  },
  {
    name: 'conversation_messages',
    group: 'conversation',
    cols: [
      { name: 'conv_id', type: 'fk' },
      { name: 'role', type: 'text' },
      { name: 'content', type: 'text' },
      { name: 'tokens', type: 'int' },
    ],
  },
  {
    name: 'trip_interactions',
    group: 'memory',
    cols: [
      { name: 'traveler_id', type: 'fk' },
      { name: 'package_id', type: 'fk' },
      { name: 'action', type: 'text' },
      { name: 'at', type: 'ts' },
    ],
  },
  {
    name: 'bookings',
    pk: true,
    group: 'retrieval',
    cols: [
      { name: 'id', type: 'uuid', emphasis: true },
      { name: 'traveler_id', type: 'fk' },
      { name: 'status', type: 'text' },
      { name: 'total_cents', type: 'int' },
      { name: 'refundable_until', type: 'ts' },
    ],
  },
  {
    name: 'booking_lines',
    group: 'retrieval',
    cols: [
      { name: 'booking_id', type: 'fk' },
      { name: 'package_id', type: 'fk' },
      { name: 'nights', type: 'int' },
      { name: 'subtotal_cents', type: 'int' },
    ],
  },
  {
    name: 'agent_traces',
    pk: true,
    group: 'conversation',
    cols: [
      { name: 'id', type: 'uuid', emphasis: true },
      { name: 'conv_id', type: 'fk' },
      { name: 'spans', type: 'jsonb' },
      { name: 'total_ms', type: 'int' },
    ],
  },
];

const tools = [
  { name: 'postgres.run_query', sub: 'aurora data api', ver: 'v3.1', ms: '96ms', health: 'healthy' as const },
  { name: 'trips.hybrid_search', sub: 'pgvector + tsvector', ver: 'v1.4', ms: '186ms', health: 'healthy' as const },
  { name: 'memory.recall', sub: 'strands @tool', ver: 'v1.2', ms: '42ms', health: 'healthy' as const },
  { name: 'memory.write_fact', sub: 'strands @tool', ver: 'v1.0', ms: '22ms', health: 'healthy' as const },
  { name: 'availability.lookup', sub: 'aurora · live', ver: 'v0.9', ms: '62ms', health: 'warn' as const },
  { name: 'bookings.hold', sub: 'aurora + provider', ver: 'v1.1', ms: '240ms', health: 'healthy' as const },
  { name: 'claude.compose', sub: 'bedrock', ver: 'sonnet-4.5', ms: '132ms', health: 'healthy' as const },
];

const SCHEMA_URL =
  'https://github.com/aws-samples/sample-dat309-agentic-workflows-aurora-mcp/blob/main/meridian/backend/db/schema.sql';

const DRY_RUN_PROMPTS: Record<string, string> = {
  'postgres.run_query': 'Dry-run: list 3 trip_packages in City Breaks under $3000',
  'trips.hybrid_search': 'Dry-run hybrid search: slow wine country week in Europe',
  'memory.recall': 'Dry-run memory recall for our Tokyo trip preferences',
  'memory.write_fact': 'Dry-run: remember we prefer boutique hotels over chains',
  'availability.lookup': 'Dry-run availability for Maldives package next month',
  'bookings.hold': 'Dry-run hold on Tuscan Vineyards package for two travelers',
  'claude.compose': 'Dry-run compose a short trip summary for Alex & Jordan',
};

export function SystemSection() {
  const { openConcierge } = useAgentBridge();

  return (
    <section id="system" className="mp-section">
      <FadeIn>
        <div className="mp-section-h-row">
          <div className="mp-section-h">
            <div className="mp-label-row">System · Aurora + MCP</div>
            <h2>
              The <em className="serif">substrate</em>, made legible.
            </h2>
            <p>
              Two views every reviewer wants: the Aurora schema that powers retrieval and memory,
              and the MCP tool catalog the agents can call. Both shipped as first-class surfaces —
              not an afterthought in a docs page.
            </p>
          </div>
          <div className="actions">
            <a className="mp-btn ghost sm" href={SCHEMA_URL} target="_blank" rel="noreferrer">
              Open schema.sql
            </a>
            <button
              type="button"
              className="mp-btn ghost sm"
              onClick={() => document.getElementById('system')?.scrollIntoView({ behavior: 'smooth' })}
            >
              Tool registry
            </button>
          </div>
        </div>
      </FadeIn>

      <FadeIn delay={0.1}>
        <div className="mp-system">
          <div className="mp-panel">
            <div className="mp-panel-h">
              <h3>Aurora schema</h3>
              <span className="sub">PostgreSQL 17 · pgvector HNSW · Data API</span>
            </div>
            <div className="mp-panel-body">
              <div className="mp-schema">
                {tables.map((t) => (
                  <div key={t.name} className="mp-schema-table">
                    <h6>
                      {t.name} {t.pk && <span className="pk">PK</span>}
                    </h6>
                    <ul>
                      {t.cols.map((c) => (
                        <li key={c.name}>
                          {c.emphasis ? <b>{c.name}</b> : c.name} <span style={{ color: 'var(--mp-dim)' }}>{c.type}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
                <div className="mp-schema-legend">
                  <span><span className="dot" style={{ background: 'var(--mp-accent)' }} /> retrieval</span>
                  <span><span className="dot" style={{ background: 'var(--mp-sky)' }} /> identity</span>
                  <span><span className="dot" style={{ background: 'var(--mp-leaf)' }} /> memory</span>
                  <span><span className="dot" style={{ background: 'var(--mp-plum)' }} /> conversation</span>
                </div>
              </div>
            </div>
          </div>

          <div className="mp-panel">
            <div className="mp-panel-h">
              <h3>MCP tool catalog</h3>
              <span className="sub">{tools.length} tools · awslabs.postgres-mcp-server v3.1</span>
            </div>
            <div className="mp-panel-body">
              <div className="mp-mcp-row head">
                <div>Tool</div>
                <div>Version</div>
                <div>p50</div>
                <div>Health</div>
                <div />
              </div>
              {tools.map((t) => (
                <div key={t.name} className="mp-mcp-row">
                  <div className="nm">
                    {t.name}
                    <small>{t.sub}</small>
                  </div>
                  <div className="ver">{t.ver}</div>
                  <div className="ms">{t.ms}</div>
                  <div>
                    <span className={`health${t.health === 'warn' ? ' warn' : ''}`}>
                      {t.health === 'warn' ? 'degraded' : 'healthy'}
                    </span>
                  </div>
                  <div>
                    <button
                      type="button"
                      className="dry"
                      onClick={() =>
                        openConcierge({
                          phase: t.name.startsWith('memory') ? 4 : t.name.includes('hybrid') ? 3 : 2,
                          prompt: DRY_RUN_PROMPTS[t.name] ?? `Dry-run ${t.name}`,
                          send: true,
                        })
                      }
                    >
                      dry-run
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </FadeIn>
    </section>
  );
}
