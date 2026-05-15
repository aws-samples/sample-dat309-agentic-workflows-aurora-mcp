/**
 * HeroSection — Meridian Pro editorial hero with live featured trip card.
 */
import { useEffect, useMemo, useState } from 'react';
import { useAgentBridge } from '../context/AgentBridge';
import { fetchProducts } from '../api/client';
import type { Product } from '../types';

interface HeroSectionProps {
  scrollY: number;
}

const FEATURE_IDS = ['CTY-001', 'BCH-001', 'ADV-001', 'WEL-001', 'CTY-002', 'BCH-004'];
const ROTATE_MS = 6000;

const matchLines: Record<string, string> = {
  'City Breaks':
    'Walkable old town · refundable rate · vegetarian dinners reservable 4 of 6 nights.',
  'Beach & Resort':
    'Adults-only stretch · 1-stop transfer · matches "slow + warm" memory facts.',
  'Adventure & Outdoors':
    'Mountain refuges with refundable holds · matches "refundable + active" preference.',
  'Wellness & Luxury':
    'Spa with daily yoga · slow pace · matches dietary + boutique preferences.',
  'Business travel':
    'Lounge access on layover · early arrival · matches aisle preference.',
};

export function HeroSection({ scrollY: _scrollY }: HeroSectionProps) {
  const { openConcierge } = useAgentBridge();
  const [items, setItems] = useState<Product[]>([]);
  const [index, setIndex] = useState(0);

  useEffect(() => {
    fetchProducts(undefined, 30, false)
      .then((all) => {
        const picks = FEATURE_IDS.map((id) => all.find((p) => p.product_id === id)).filter(
          (p): p is Product => Boolean(p),
        );
        setItems(picks.length > 0 ? picks : all.slice(0, 6));
      })
      .catch(() => {
        // Backend offline — surface a graceful empty state with the placeholder card
      });
  }, []);

  useEffect(() => {
    if (items.length < 2) return;
    const t = setInterval(() => setIndex((i) => (i + 1) % items.length), ROTATE_MS);
    return () => clearInterval(t);
  }, [items.length]);

  const current = items[index];
  const matchBecause = useMemo(() => {
    if (!current) {
      return 'Match because: matches "slow + wine country", refundable, veg dinners reservable 4 of 6 nights.';
    }
    const tail = matchLines[current.category] ?? 'matches your stored memory facts.';
    return `Match because: ${tail}`;
  }, [current]);

  const tripId = current ? current.product_id.toLowerCase() : 'trip_2614';

  return (
    <section className="mp-hero">
      <div>
        <div className="mp-label-row">Meridian — agentic travel concierge</div>
        <h1>
          Plan. <em className="serif">Fly.</em> Land.
        </h1>
        <p className="lede">
          A travel concierge that understands what you actually mean. Built on Aurora PostgreSQL,
          MCP, and Cohere Embed v4 — so &ldquo;a slow week somewhere we can drink good wine&rdquo;
          returns the right hotel, the right flight, the right neighborhood. Every step traced.
          Every fact remembered.
        </p>
        <div className="mp-hero-cta">
          <button
            type="button"
            className="mp-btn primary"
            onClick={() => openConcierge({ phase: 4, focus: true })}
          >
            Talk to concierge
          </button>
          <button
            type="button"
            className="mp-btn ghost"
            onClick={() => document.getElementById('products')?.scrollIntoView({ behavior: 'smooth' })}
          >
            Browse trips
          </button>
        </div>
        <div className="mp-hero-stats">
          <div className="mp-stat"><b>30</b>curated packages</div>
          <div className="mp-stat"><b>4</b>orchestration modes</div>
          <div className="mp-stat"><b>1024d</b>Cohere v4</div>
          <div className="mp-stat"><b>~340ms</b>p50 latency</div>
          <div className="mp-stat"><b>OTel</b>trace export</div>
        </div>
      </div>

      <div
        className="mp-feature mp-feature-clickable"
        role="button"
        tabIndex={0}
        onClick={() =>
          current &&
          openConcierge({
            phase: 4,
            prompt: `We're planning ${current.name}. What should we know before booking?`,
            send: true,
          })
        }
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            current &&
              openConcierge({
                phase: 4,
                prompt: `We're planning ${current.name}. What should we know before booking?`,
                send: true,
              });
          }
        }}
      >
        <div className="mp-feature-top">
          <div className="id">
            Currently planning <b>· {tripId}</b>
          </div>
          <div className="badge">held · 12h</div>
        </div>
        <div className="mp-feature-scene">
          {current?.image_url ? (
            <img src={current.image_url} alt={current.name} />
          ) : null}
          <div className="mp-feature-ribbon">
            <div>
              <strong>{current?.name ?? 'Tuscan Vineyards · 7 nights'}</strong>
              <span>
                {current
                  ? `${current.brand} · ${current.category}`
                  : 'Florence + Chianti · May 14–21 · two travelers'}
              </span>
            </div>
            <div className="price">${(current?.price ?? 2840).toFixed(0)}</div>
          </div>
        </div>
        <div className="mp-feature-meta">
          <div className="cell">
            From<b>BOS</b>
          </div>
          <div className="cell">
            Hotel<b>{current?.brand ?? 'Borgo San Felice'}</b>
          </div>
          <div className="cell">
            Refundable<b>Until May 11</b>
          </div>
        </div>
        <div className="mp-feature-why">
          <div className="quote">
            <em>{matchBecause.split(':')[0]}:</em>
            {matchBecause.includes(':') ? matchBecause.slice(matchBecause.indexOf(':') + 1) : ''}
            <div className="src">grounded in your memory · 8 traveler facts · 2 prior trips</div>
          </div>
        </div>
      </div>
    </section>
  );
}
