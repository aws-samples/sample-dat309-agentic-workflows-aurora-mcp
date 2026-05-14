/**
 * Footer — Daylight Studio credits
 */
export function Footer() {
  return (
    <footer
      style={{
        padding: '40px 28px 56px',
        maxWidth: 1180,
        margin: '0 auto',
        borderTop: '1px solid var(--dl-line)',
        fontSize: 12,
        color: 'var(--dl-dim)',
        lineHeight: 1.8,
      }}
    >
      <b style={{ color: 'var(--dl-ink)' }}>Meridian</b> — Plan. Fly. Land. · © Shayon Sanyal
      <br />
      <span style={{ fontFamily: "'SF Mono', monospace", fontSize: 11 }}>
        Aurora PostgreSQL 17 · pgvector 0.8 · AgentCore · Strands · MCP · Claude · Cohere Embed v4
      </span>
    </footer>
  );
}
