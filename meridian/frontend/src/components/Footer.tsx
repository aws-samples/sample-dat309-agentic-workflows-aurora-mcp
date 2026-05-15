/**
 * Footer — Meridian Pro pull-quote band + minimal footer
 */
export function Footer() {
  return (
    <>
      <div className="mp-pull">
        <blockquote>
          The trip you describe in a paragraph; the concierge <span>watches</span> it for weeks.
        </blockquote>
        <cite>The thesis for Meridian</cite>
      </div>
      <footer className="mp-foot">
        <div>
          <b>Meridian Pro · 2026.1</b> — light theme, professional. Daylight Studio tokens evolved
          with cooler neutrals, a tighter type scale, and a workspace-grade agent UI.
        </div>
        <div>Aurora · pgvector · MCP · Strands · Cohere Embed v4</div>
      </footer>
    </>
  );
}
