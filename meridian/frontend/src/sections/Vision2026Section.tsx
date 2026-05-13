/**
 * Vision2026Section — session narrative: memory, MCP, AgentCore runtime, orchestration
 */
import { FadeIn } from '../components/FadeIn';
import { MemoryChip } from '../components/MemoryChip';

const pillars = [
  {
    num: '01',
    title: 'Contextual',
    serif: 'memory',
    desc: 'Short-term turn context in the agent runtime. Long-term facts in Aurora with pgvector — party size, travel dates, dietary needs — recalled before every search.',
    tags: ['Session state', 'memory.facts', 'pgvector recall'],
  },
  {
    num: '02',
    title: 'MCP',
    serif: 'servers',
    desc: 'Model Context Protocol exposes Aurora tools with discovery, schemas, and IAM auth — so agents never hardcode SQL or connection strings.',
    tags: ['Tool catalog', 'RDS Data API', 'Secure connect'],
  },
  {
    num: '03',
    title: 'Agent',
    serif: 'runtime',
    desc: 'Bedrock AgentCore hosts durable, governed execution. LangGraph models supervisor graphs. Strands Agents wire tools to Claude on Bedrock.',
    tags: ['AgentCore', 'LangGraph', 'Strands SDK'],
  },
  {
    num: '04',
    title: 'Multi-agent',
    serif: 'workflows',
    desc: 'Supervisor routes to Search, Availability, Policy, and Booking specialists — multi-turn itineraries that read live package data from Aurora.',
    tags: ['Supervisor', 'Specialists', 'Multi-turn'],
  },
  {
    num: '05',
    title: 'Trace-first',
    serif: 'observability',
    desc: 'Every span is permalinked: agent, tool, SQL, latency, token spend. Replay traces without re-running the LLM.',
    tags: ['agent_traces', 'Replay', 'Permalinks'],
  },
  {
    num: '06',
    title: 'Governed',
    serif: 'autonomy',
    desc: 'Plans surface before commit — budgets, scopes, confirm-before-charge. Autonomy with guardrails on real money and inventory.',
    tags: ['Plan → confirm', 'Scopes', 'Policy agent'],
  },
];

const runtimeStack = [
  { label: 'Orchestration', value: 'LangGraph · Strands supervisor' },
  { label: 'Runtime', value: 'Amazon Bedrock AgentCore' },
  { label: 'Models', value: 'Claude on Bedrock · Cohere Embed v4' },
  { label: 'Data plane', value: 'Aurora PostgreSQL · MCP · RDS Data API' },
];

export function Vision2026Section() {
  return (
    <section
      id="vision2026"
      style={{
        padding: '64px 28px',
        maxWidth: 1180,
        margin: '0 auto',
        borderTop: '1px solid var(--dl-line)',
      }}
    >
      <FadeIn>
        <div style={{ marginBottom: 40 }}>
          <span className="section-label">DAT309 · 2026</span>
          <h2 className="section-headline">
            Memory, runtime, and <em className="serif">orchestration</em>.
          </h2>
          <p className="section-subtitle" style={{ maxWidth: 680 }}>
            Build agentic workflows with Aurora and MCP — contextual memory, multi-turn queries,
            and multi-agent orchestration on Amazon Bedrock AgentCore, LangGraph, and Strands Agents.
          </p>
        </div>
      </FadeIn>

      <FadeIn delay={0.05}>
        <div className="runtime-strip">
          {runtimeStack.map((row) => (
            <div key={row.label} className="runtime-strip-row">
              <span className="runtime-strip-label">{row.label}</span>
              <span className="runtime-strip-value">{row.value}</span>
            </div>
          ))}
        </div>
      </FadeIn>

      <FadeIn delay={0.1}>
        <div className="memory-preview-card">
          <div>
            <div className="memory-preview-eyebrow">Wave 01 · Memory of me</div>
            <p className="memory-preview-copy">
              Agents recall durable traveler facts from Aurora before routing — so
              &ldquo;beach escape in October&rdquo; respects party size, dates, and dietary needs across turns.
            </p>
          </div>
          <MemoryChip onInspect={() => document.getElementById('agent')?.scrollIntoView({ behavior: 'smooth' })} />
        </div>
      </FadeIn>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: 16,
          marginTop: 28,
        }}
      >
        {pillars.map((p, i) => (
          <FadeIn key={p.num} delay={0.12 + i * 0.04}>
            <article className="vision-pillar">
              <span className="vision-pillar-num">Pillar {p.num}</span>
              <h3 className="vision-pillar-title">
                {p.title} <em className="serif">{p.serif}</em>
              </h3>
              <p className="vision-pillar-desc">{p.desc}</p>
              <div className="vision-pillar-tags">
                {p.tags.map((t) => (
                  <span key={t} className="phase-tag">
                    {t}
                  </span>
                ))}
              </div>
            </article>
          </FadeIn>
        ))}
      </div>

      <FadeIn delay={0.35}>
        <p className="vision-footnote">
          Today&apos;s demo climbs Phases 1–4 on the Meridian concierge. Phase 4 adds memory and AgentCore
          on top of Phase 3&apos;s semantic search — the ladder, not a separate product.
        </p>
      </FadeIn>
    </section>
  );
}
