/**
 * Footer component with credits and tech stack
 */
export function Footer() {
  return (
    <footer
      style={{
        padding: '40px 40px',
        background: '#060a14',
        borderTop: '1px solid rgba(255,255,255,0.04)',
        textAlign: 'center',
      }}
    >
      <div
        style={{
          fontSize: 13,
          color: '#334155',
          lineHeight: 2,
          fontFamily: "'SF Pro Text', sans-serif",
        }}
      >
        <span style={{ color: '#64748b', fontWeight: 500 }}>ClickShop</span> — Agentic Commerce Demo
        <br />
        <span style={{ fontFamily: "'SF Mono', monospace", fontSize: 11 }}>
          Aurora PostgreSQL 17.5 · pgvector 0.8 · Strands SDK · Nova Multimodal · Claude Sonnet 4.5 · MCP
        </span>
      </div>
    </footer>
  );
}
