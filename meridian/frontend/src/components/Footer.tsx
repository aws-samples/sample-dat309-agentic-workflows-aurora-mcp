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
      <b style={{ color: 'var(--dl-ink)' }}>Meridian</b> — Ask. Shop. Done. · © Shayon Sanyal
      <br />
      <span style={{ fontFamily: "'SF Mono', monospace", fontSize: 11 }}>
        Aurora PostgreSQL 17.5 · pgvector 0.8 · Strands SDK · Cohere Embed v4 · Claude Opus 4.7 · MCP
      </span>
    </footer>
  );
}
