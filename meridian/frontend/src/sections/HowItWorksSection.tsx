/**
 * HowItWorksSection — Daylight Studio pillar cards for four phases
 */
import { FadeIn } from '../components/FadeIn';

interface Phase {
  num: string;
  title: string;
  serifWord: string;
  subtitle: string;
  beat: string;
  desc: string;
  code: string;
  tags: string[];
  flow: string;
  scale: string;
}

const phases: Phase[] = [
  {
    num: '01',
    title: 'Direct',
    serifWord: 'filters',
    subtitle: 'The lab',
    beat: 'Looks up trips by exact type, operator, or price — like reading a brochure.',
    scale: '50 bookings/day',
    desc: 'One Strands agent calls Aurora through the RDS Data API with hardcoded tools. Fast to ship, easy to demo — but &ldquo;romantic week in Italy&rdquo; won&apos;t work until Phase 3.',
    code: `agent = Agent(
  model=BedrockModel("claude-opus-4-7"),
  tools=[search_packages, check_dates, book_trip]
)
agent("City breaks under $2000")`,
    tags: ['Strands SDK', 'RDS Data API', 'SQL filters', 'Aurora PostgreSQL'],
    flow: 'Traveler → Agent → RDS Data API → Aurora',
  },
  {
    num: '02',
    title: 'MCP',
    serifWord: 'tools',
    subtitle: 'The toolkit',
    beat: 'Same catalog queries — but tools are exposed via MCP instead of hardcoded in the agent.',
    scale: '5K bookings/day',
    desc: 'The agent calls Aurora through postgres-mcp-server instead of baking SQL into code. RDS Data API removes connection pools; Serverless v2 scales to zero between sessions.',
    code: `mcp = MCPClient(awslabs.postgres_mcp_server)
tools = mcp.list_tools()  # execute_sql, describe…
→ Aurora Serverless v2 · IAM auth`,
    tags: ['MCP', 'postgres-mcp', 'Serverless v2', 'IAM Auth'],
    flow: 'Traveler → Agent → MCP → Data API → Aurora',
  },
  {
    num: '03',
    title: 'Specialist',
    serifWord: 'agents',
    subtitle: 'Semantic scale',
    beat: 'Natural language works — a supervisor routes to search, availability, and booking specialists.',
    scale: '50K bookings/day',
    desc: 'Cohere Embed v4 vectors in pgvector power hybrid semantic + lexical search. A Strands supervisor delegates to specialist agents so vague requests map to real packages.',
    code: `emb = cohere_embed("romantic week in Italy")
SELECT *, 0.7*semantic + 0.3*lexical AS score
FROM packages ORDER BY score DESC LIMIT 5`,
    tags: ['Cohere Embed v4', 'pgvector 0.8', 'Strands supervisor', 'Hybrid search'],
    flow: 'Traveler → Supervisor → [Search · Availability · Booking] → Aurora',
  },
  {
    num: '04',
    title: 'Personal',
    serifWord: 'memory',
    subtitle: 'Production',
    beat: 'Remembers the traveler — party size, dates, allergies — before every search and booking.',
    scale: '50K+ bookings/day',
    desc: 'Bedrock AgentCore hosts durable sessions. Short-term turn context plus long-term facts in Aurora feed the same specialist agents — with governed plan→confirm flows and permalinked traces.',
    code: `session = AgentCore.start(trace_id=tr)
facts = memory.recall(user_id, embed(query))
concierge = ConciergeOrchestrator(memory=session + facts)
result = concierge.run(query)`,
    tags: ['AgentCore', 'memory.facts', 'Trace replay', 'Plan → confirm'],
    flow: 'Traveler → AgentCore → Memory → Supervisor → MCP → Aurora',
  },
];

export function HowItWorksSection() {
  return (
    <section
      id="howitworks"
      style={{
        padding: '64px 28px',
        maxWidth: 1280,
        margin: '0 auto',
        borderTop: '1px solid var(--dl-line)',
      }}
    >
      <FadeIn>
        <div style={{ marginBottom: 40 }}>
          <span className="section-label">Architecture</span>
          <h2 className="section-headline">
            Four phases. One <em className="serif">ladder</em>.
          </h2>
          <p className="section-subtitle">
            Each phase adds exactly one capability: <strong>filters</strong> → <strong>MCP tools</strong> →{' '}
            <strong>semantic search</strong> → <strong>memory</strong>. Phases 1–3 are the teaching path;
            Phase 4 is how Meridian runs in production.
          </p>
        </div>
      </FadeIn>

      <div className="howitworks-grid">
        {phases.map((p, i) => (
          <FadeIn key={p.num} delay={i * 0.08}>
            <div className="phase-card">
              <span className="phase-subtitle">Phase {p.num} · {p.subtitle}</span>
              <h3 className="phase-title" style={{ margin: '8px 0 8px' }}>
                {p.title}
                <em className="serif"> {p.serifWord}</em>
              </h3>
              <p className="phase-desc" style={{ fontWeight: 500, color: 'var(--dl-ink)', marginBottom: 8 }}>
                {p.beat}
              </p>
              <div className="phase-flow">{p.flow}</div>
              <p className="phase-desc">{p.desc}</p>
              <div className="phase-code">{p.code}</div>
              <div className="phase-footer">
                <div className="phase-tags">
                  {p.tags.map((t) => (
                    <span key={t} className="phase-tag">
                      {t}
                    </span>
                  ))}
                </div>
                <div className="phase-metrics">
                  <span>↗ {p.scale}</span>
                </div>
              </div>
            </div>
          </FadeIn>
        ))}
      </div>

      <FadeIn delay={0.35}>
        <div className="horizon-callout">
          <span className="horizon-callout-label">Try the ladder</span>
          <p>
            Start at Phase 1 with &ldquo;city breaks&rdquo; — then try the same intent in Phase 3 as
            &ldquo;romantic weekend in Europe.&rdquo; Jump to{' '}
            <strong>Phase 4 · Memory</strong> to see AgentCore, session context, and Aurora facts in the trace —{' '}
            <button
              type="button"
              className="horizon-callout-link"
              onClick={() => document.getElementById('agent')?.scrollIntoView({ behavior: 'smooth' })}
            >
              open the demo →
            </button>
          </p>
        </div>
      </FadeIn>
    </section>
  );
}
