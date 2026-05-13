/**
 * StickyNav — Daylight Studio top bar with brand mark
 */
interface StickyNavProps {
  scrollY: number;
}

const navLinks = [
  { label: 'Catalog', target: 'products' },
  { label: 'How it works', target: 'howitworks' },
  { label: 'Agent', target: 'agent' },
];

export function StickyNav({ scrollY }: StickyNavProps) {
  const solid = scrollY > 40;

  return (
    <nav className={`dl-nav${solid ? ' solid' : ''}`}>
      <div className="dl-brand">
        <div className="dl-brand-mark" />
        Meridian
      </div>

      <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
        <div style={{ display: 'flex', gap: 22 }}>
          {navLinks.map((n) => (
            <button
              key={n.target}
              onClick={() => document.getElementById(n.target)?.scrollIntoView({ behavior: 'smooth' })}
              className="nav-link"
            >
              {n.label}
            </button>
          ))}
        </div>
        <button
          className="nav-cta"
          onClick={() => document.getElementById('agent')?.scrollIntoView({ behavior: 'smooth' })}
        >
          Try the agent →
        </button>
      </div>
    </nav>
  );
}
