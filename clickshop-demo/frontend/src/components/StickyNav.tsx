/**
 * StickyNav - Fixed navigation with frosted glass effect
 * Wordmark fades in after scrolling past hero
 */
interface StickyNavProps {
  scrollY: number;
}

const navLinks = [
  { label: 'Products', target: 'products' },
  { label: 'How It Works', target: 'howitworks' },
  { label: 'Try It', target: 'agent' },
];

export function StickyNav({ scrollY }: StickyNavProps) {
  const showBackground = scrollY > 80;

  return (
    <nav
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 100,
        padding: '0 40px',
        height: 56,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: showBackground ? 'rgba(6,10,20,0.85)' : 'transparent',
        backdropFilter: showBackground ? 'blur(20px)' : 'none',
        borderBottom: showBackground
          ? '1px solid rgba(255,255,255,0.04)'
          : '1px solid transparent',
        transition: 'all 0.3s',
      }}
    >
      {/* Wordmark */}
      <span
        style={{
          fontSize: 16,
          fontWeight: 700,
          color: '#f1f5f9',
          letterSpacing: '-0.02em',
          fontFamily: "'SF Pro Display', -apple-system, sans-serif",
          opacity: showBackground ? 1 : 0,
          transition: 'opacity 0.3s',
        }}
      >
        ClickShop
      </span>

      {/* Nav links */}
      <div style={{ display: 'flex', gap: 32 }}>
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

      {/* Spacer for balance */}
      <div style={{ width: 80 }} />
    </nav>
  );
}
