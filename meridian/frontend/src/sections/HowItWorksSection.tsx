/**
 * HowItWorksSection — Daylight Studio pillar cards for three phases
 */
import { FadeIn } from '../components/FadeIn';

interface Phase {
  num: string;
  title: string;
  serifWord: string;
  subtitle: string;
  desc: string;
  code: string;
  tags: string[];
  flow: string;
  scale: string;
}

const phases: Phase[] = [
  {
    num: '01',
    title: 'Single',
    serifWord: 'agent',
    subtitle: 'The Prototype',
    scale: '50 orders/day',
    desc: 'One Strands agent with direct database access via RDS Data API. Simple, fast to build — every tool is hardcoded and the agent manages all operations directly.',
    code: `agent = Agent(
  model=BedrockModel("global.anthropic.claude-opus-4-7-v1"),
  tools=[search_products, check_inventory, process_order]
)
result = agent("Find comfortable running shoes")`,
    tags: ['Strands SDK', 'Claude Opus 4.7', 'RDS Data API', 'Aurora PostgreSQL'],
    flow: 'User → Agent → RDS Data API → Aurora PostgreSQL',
  },
  {
    num: '02',
    title: 'Agent +',
    serifWord: 'MCP',
    subtitle: 'The Standard',
    scale: '5K orders/day',
    desc: 'The agent discovers database capabilities through MCP instead of hardcoding them. RDS Data API eliminates connection management. Aurora Serverless v2 scales to zero when idle.',
    code: `mcp = MCPClient(awslabs.postgres_mcp_server)
  → resource_arn: meridian-demo
  → Serverless v2 (0.5–64 ACUs)
  → RDS Data API + IAM auth`,
    tags: ['MCP', 'RDS Data API', 'Serverless v2', 'IAM Auth'],
    flow: 'User → Agent → MCP → Data API → Aurora Serverless',
  },
  {
    num: '03',
    title: 'Multi-',
    serifWord: 'agent',
    subtitle: 'Production',
    scale: '50K orders/day',
    desc: 'A supervisor routes to specialized agents. Search uses Cohere Embed v4 embeddings stored in pgvector — semantic search with 1024-dimensional vectors and HNSW indexing.',
    code: `emb = cohere_embed(text="marathon shoes")
SELECT *, 1-(embedding <=> $1) AS similarity
FROM products ORDER BY embedding <=> $1 LIMIT 5`,
    tags: ['Cohere Embed v4', 'pgvector 0.8', 'HNSW', 'Multi-Agent'],
    flow: 'User → Supervisor → [Search | Product | Order] → Aurora + pgvector',
  },
];

export function HowItWorksSection() {
  return (
    <section
      id="howitworks"
      style={{
        padding: '64px 28px',
        maxWidth: 1180,
        margin: '0 auto',
        borderTop: '1px solid var(--dl-line)',
      }}
    >
      <FadeIn>
        <div style={{ marginBottom: 40 }}>
          <span className="section-label">Architecture</span>
          <h2 className="section-headline">
            Three phases. One <em className="serif">evolution</em>.
          </h2>
          <p className="section-subtitle">
            Same application, three architectures. Watch complexity decrease as capability increases.
          </p>
        </div>
      </FadeIn>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: 20,
        }}
      >
        {phases.map((p, i) => (
          <FadeIn key={p.num} delay={i * 0.1}>
            <div className="phase-card">
              <span className="phase-subtitle">Phase {p.num}</span>
              <h3 className="phase-title" style={{ margin: '8px 0 12px' }}>
                {p.title}
                <em className="serif"> {p.serifWord}</em>
              </h3>
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
    </section>
  );
}
