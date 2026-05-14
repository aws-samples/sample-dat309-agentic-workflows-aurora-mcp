/**
 * StickyNav — Daylight Studio top bar with brand mark
 */
interface StickyNavProps {
  scrollY: number;
}

const navLinks = [
  { label: 'Trips', target: 'products' },
  { label: 'How it works', target: 'howitworks' },
  { label: 'Deep dive', target: 'vision2026' },
  { label: 'Agent', target: 'agent' },
];

export function StickyNav({ scrollY }: StickyNavProps) {
  const solid = scrollY > 40;

  return (
    <nav className={`dl-nav${solid ? ' solid' : ''}`}>
      <div className="dl-brand">
        <svg className="dl-brand-mark" viewBox="0 0 24 24" aria-hidden="true">
          <rect width="24" height="24" rx="6" fill="currentColor" />
          <path
            fill="#ff5b1f"
            d="M4.5 12.2c-.2-.6.3-1.2.9-1.3l6.8-2 1.5-3.2c.2-.6.9-.8 1.4-.3l1.8 1.5 6.2 1.8c.8.2 1.2 1.1.9 1.8s-1.1 1.2-1.9.9l-6.2-1.8-1.8 1.5c-.5.4-1.2.2-1.4-.3l-1.5-3.2-6.8 2c-.6.1-1.1.7-.9 1.3.2.5.7.8 1.2.8.1 0 .3 0 .4-.1l2.4-.7c.4-.1.9.1 1 .5s-.1.9-.5 1l-2.4.7c-.7.2-1.5 0-2-.6-.7-.9-.4-2.3.6-2.9z"
          />
        </svg>
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
