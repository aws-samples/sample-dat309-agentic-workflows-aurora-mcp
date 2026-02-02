/**
 * HowItWorksSection - Three phase architecture cards
 * Features alternating slide-in animations and code blocks
 */
import { FadeIn } from '../components/FadeIn';

interface Phase {
  num: string;
  title: string;
  subtitle: string;
  color: string;
  time: string;
  scale: string;
  desc: string;
  code: string;
  tags: string[];
  flow: string;
}

const phases: Phase[] = [
  {
    num: '01',
    title: 'Single Agent',
    subtitle: 'The Prototype',
    color: '#3b82f6',
    time: '~100ms',
    scale: '50 orders/day',
    desc: 'One Strands agent with direct database access via RDS Data API. Simple, fast to build — every tool is hardcoded and the agent manages all operations directly.',
    code: `agent = Agent(
  model=BedrockModel("global.anthropic.claude-sonnet-4-5-20250929-v1:0"),
  tools=[search_products, check_inventory, process_order]
)
result = agent("Find comfortable running shoes")`,
    tags: ['Strands SDK', 'Claude Sonnet 4.5', 'RDS Data API', 'Aurora PostgreSQL'],
    flow: 'User → Agent → RDS Data API → Aurora PostgreSQL',
  },
  {
    num: '02',
    title: 'Agent + MCP',
    subtitle: 'The Standard',
    color: '#a855f7',
    time: '~100ms',
    scale: '5K orders/day',
    desc: 'The agent discovers database capabilities through MCP instead of hardcoding them. RDS Data API eliminates connection management. Aurora Serverless v2 scales to zero when idle.',
    code: `mcp = MCPClient(awslabs.postgres_mcp_server)
  → resource_arn: agentstride-demo
  → Serverless v2 (0–64 ACUs)
  → RDS Data API + IAM auth
  → Zero connection management`,
    tags: ['MCP', 'RDS Data API', 'Serverless v2', 'IAM Auth', 'Secrets Manager'],
    flow: 'User → Agent → MCP → Data API → Aurora Serverless',
  },
  {
    num: '03',
    title: 'Multi-Agent',
    subtitle: 'Production',
    color: '#10b981',
    time: '~350ms',
    scale: '50K orders/day',
    desc: 'A supervisor routes to specialized agents. Search uses Nova Multimodal embeddings stored in pgvector — the same index handles both text queries and product image uploads.',
    code: `# Text AND image → same 1024-dim vector space
emb = nova_embed(text="marathon shoes")   # or
emb = nova_embed(image=photo_bytes)       # same index!

SELECT *, 1-(embedding <=> $1) AS similarity
FROM products ORDER BY embedding <=> $1`,
    tags: ['Nova Multimodal', 'pgvector 0.8', 'HNSW', '1024-dim', 'Image Search', 'Multi-Agent'],
    flow: 'User → Supervisor → [Search | Product | Order] → Aurora + pgvector',
  },
];

export function HowItWorksSection() {
  return (
    <section
      id="howitworks"
      style={{
        position: 'relative',
        padding: '120px 40px',
        background: 'linear-gradient(180deg, #060a14, #0c1222, #060a14)',
      }}
    >
      <div style={{ maxWidth: 960, margin: '0 auto' }}>
        {/* Header */}
        <FadeIn>
          <div style={{ textAlign: 'center', marginBottom: 80 }}>
            <span className="section-label" style={{ color: '#a855f7' }}>
              Architecture
            </span>
            <h2 className="section-headline">Three phases. One evolution.</h2>
            <p className="section-subtitle" style={{ maxWidth: 500 }}>
              Same application, three architectures. Watch complexity decrease as capability
              increases.
            </p>
          </div>
        </FadeIn>

        {/* Phase cards */}
        {phases.map((p, i) => (
          <FadeIn key={i} delay={i * 0.15} direction={i % 2 === 0 ? 'left' : 'right'}>
            <div className="phase-card" style={{ marginBottom: i < 2 ? 48 : 0 }}>
              {/* Top accent line */}
              <div
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  height: 2,
                  background: `linear-gradient(90deg, transparent, ${p.color}60, transparent)`,
                }}
              />

              <div style={{ display: 'flex', alignItems: 'flex-start', gap: 32 }}>
                {/* Phase number */}
                <div
                  style={{
                    fontSize: 64,
                    fontWeight: 800,
                    color: p.color,
                    fontFamily: "'SF Pro Display', sans-serif",
                    lineHeight: 1,
                    flexShrink: 0,
                    minWidth: 80,
                    textShadow: `0 0 40px ${p.color}60`,
                  }}
                >
                  {p.num}
                </div>

                <div style={{ flex: 1 }}>
                  {/* Title row */}
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: 16, marginBottom: 6 }}>
                    <h3 className="phase-title">{p.title}</h3>
                    <span className="phase-subtitle" style={{ color: p.color }}>
                      {p.subtitle}
                    </span>
                  </div>

                  {/* Flow diagram */}
                  <div className="phase-flow">{p.flow}</div>

                  <p className="phase-desc">{p.desc}</p>

                  {/* Code block */}
                  <div className="phase-code" style={{ borderLeftColor: `${p.color}50` }}>
                    {p.code}
                  </div>

                  {/* Tags + metrics */}
                  <div className="phase-footer">
                    <div className="phase-tags">
                      {p.tags.map((t) => (
                        <span
                          key={t}
                          className="phase-tag"
                          style={{
                            background: `${p.color}10`,
                            color: p.color,
                            border: `1px solid ${p.color}20`,
                          }}
                        >
                          {t}
                        </span>
                      ))}
                    </div>
                    <div className="phase-metrics">
                      <span>⏱ {p.time}</span>
                      <span>↗ {p.scale}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </FadeIn>
        ))}
      </div>
    </section>
  );
}
