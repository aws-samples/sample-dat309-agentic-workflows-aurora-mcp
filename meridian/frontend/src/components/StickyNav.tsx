/**
 * StickyNav — Meridian Pro top bar with brand mark, segmented nav, status dot
 */
import { useEffect, useState } from 'react';

interface StickyNavProps {
  scrollY: number;
}

const navLinks = [
  { label: 'Concierge', target: 'agent' },
  { label: 'Trips', target: 'products' },
  { label: 'How it works', target: 'howitworks' },
  { label: 'Memory', target: 'memory' },
  { label: 'System', target: 'system' },
];

type Health = 'healthy' | 'checking' | 'down';

export function StickyNav({ scrollY: _scrollY }: StickyNavProps) {
  const [active, setActive] = useState<string>('agent');
  const [health, setHealth] = useState<Health>('checking');

  // Backend health ping
  useEffect(() => {
    let timer: ReturnType<typeof setInterval> | null = null;

    const ping = async () => {
      try {
        const res = await fetch('http://localhost:8000/health');
        setHealth(res.ok ? 'healthy' : 'down');
      } catch {
        setHealth('down');
      }
    };

    ping();
    timer = setInterval(ping, 30000);
    return () => {
      if (timer) clearInterval(timer);
    };
  }, []);

  // Active section observer
  useEffect(() => {
    const ids = navLinks.map((n) => n.target);
    const sections = ids
      .map((id) => document.getElementById(id))
      .filter((el): el is HTMLElement => Boolean(el));

    if (sections.length === 0) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (visible) setActive(visible.target.id);
      },
      { rootMargin: '-30% 0px -60% 0px', threshold: [0.1, 0.4, 0.7] },
    );

    sections.forEach((s) => observer.observe(s));
    return () => observer.disconnect();
  }, []);

  const scrollTo = (id: string) =>
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });

  const statusLabel =
    health === 'healthy' ? 'Aurora · pgvector OK' : health === 'checking' ? 'Checking…' : 'Backend offline';
  const statusClass = health === 'healthy' ? '' : health === 'checking' ? 'warn' : 'err';

  return (
    <nav className="mp-topnav">
      <div className="mp-topnav-inner">
        <div className="mp-brand">
          <span className="mp-brand-glyph" />
          Meridian
          <span className="mp-brand-build">Pro · 2026.1</span>
        </div>

        <div className="mp-nav-center">
          {navLinks.map((n) => (
            <button
              key={n.target}
              type="button"
              className={`mp-nav-link${active === n.target ? ' active' : ''}`}
              onClick={() => scrollTo(n.target)}
            >
              {n.label}
            </button>
          ))}
        </div>

        <div className="mp-nav-right">
          <div className="mp-nav-meta" title={statusLabel}>
            <span className={`mp-nav-status-dot ${statusClass}`.trim()} /> {statusLabel}
          </div>
          <button className="mp-cta" onClick={() => scrollTo('agent')}>
            Talk to concierge →
          </button>
        </div>
      </div>
    </nav>
  );
}
