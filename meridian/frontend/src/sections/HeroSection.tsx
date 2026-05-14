/**
 * HeroSection — Daylight Studio editorial hero with rotating destination spotlight
 */
import { useState, useEffect } from 'react';
import { fetchProducts } from '../api/client';
import type { Product } from '../types';
import { ProductThumb } from '../components/ProductThumb';

interface HeroSectionProps {
  scrollY: number;
}

const SPOTLIGHT_IDS = ['CTY-001', 'CTY-002', 'BCH-001', 'BCH-004', 'ADV-001', 'WEL-004'];
const ROTATE_MS = 5000;

export function HeroSection({ scrollY: _scrollY }: HeroSectionProps) {
  const [spotlight, setSpotlight] = useState<Product[]>([]);
  const [index, setIndex] = useState(0);

  useEffect(() => {
    fetchProducts(undefined, 30, false)
      .then((items) => {
        const picks = SPOTLIGHT_IDS.map((id) => items.find((p) => p.product_id === id)).filter(
          (p): p is Product => Boolean(p)
        );
        setSpotlight(picks.length > 0 ? picks : items.slice(0, 6));
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (spotlight.length < 2) return;
    const timer = setInterval(() => setIndex((i) => (i + 1) % spotlight.length), ROTATE_MS);
    return () => clearInterval(timer);
  }, [spotlight.length]);

  return (
    <section style={{ padding: '100px 28px 56px', maxWidth: 1180, margin: '0 auto' }}>
      <div
        style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 40, alignItems: 'center' }}
        className="hero-grid"
      >
        <div className="hero-copy">
          <div className="dl-eyebrow">Meridian — your agentic travel concierge</div>
          <h1 className="dl-display">
            Plan.<br /><em className="serif">Fly.</em><br />Land.
          </h1>
          <p className="dl-lede" style={{ marginBottom: 16 }}>
            Understands what you actually mean — built on Aurora, MCP, and Cohere
            embeddings — so &ldquo;romantic week in Europe under $3k&rdquo; returns the right city
            break, beach escape, and rail pass. Available dates included.
          </p>
          <p className="dl-lede" style={{ marginBottom: 28, fontSize: 15, color: 'var(--dl-dim)' }}>
            Next: contextual memory, AgentCore runtime, and replayable traces — see the deep dive below.
          </p>
          <div style={{ display: 'flex', gap: 10, marginBottom: 32 }}>
            <button
              onClick={() => document.getElementById('agent')?.scrollIntoView({ behavior: 'smooth' })}
              className="hero-btn-primary"
            >
              Talk to the concierge
            </button>
            <button
              onClick={() => document.getElementById('products')?.scrollIntoView({ behavior: 'smooth' })}
              className="hero-btn-secondary"
            >
              Browse trips
            </button>
          </div>
          <div style={{ display: 'flex', gap: 28, flexWrap: 'wrap' }}>
            <div className="dl-stat"><b>30</b>packages</div>
            <div className="dl-stat"><b>6</b>trip types</div>
            <div className="dl-stat"><b>1024d</b>vectors</div>
            <div className="dl-stat"><b>~340ms</b>p50 latency</div>
          </div>
        </div>

        <div className="hero-spotlight-card">
          <div className="hero-spotlight-stage">
            {spotlight.length > 0 ? (
              spotlight.map((trip, i) => (
                <div
                  key={trip.product_id}
                  className={`hero-spotlight-slide${i === index ? ' active' : ''}`}
                  aria-hidden={i !== index}
                >
                  <ProductThumb
                    imageUrl={trip.image_url}
                    category={trip.category}
                    alt={trip.name}
                    className="hero-spotlight-image"
                    emojiSize={48}
                  />
                  <div className="hero-spotlight-overlay">
                    <div className="hero-spotlight-overlay-text">
                      <strong>{trip.name}</strong>
                      <span>{trip.brand} · {trip.category}</span>
                    </div>
                    <span className="hero-spotlight-overlay-price">${trip.price.toFixed(0)}</span>
                  </div>
                </div>
              ))
            ) : (
              <ProductThumb
                category="City Breaks"
                alt="Paris Long Weekend"
                className="hero-spotlight-image"
                emojiSize={48}
              />
            )}
          </div>
          {spotlight.length > 1 && (
            <div className="hero-spotlight-dots">
              {spotlight.map((p, i) => (
                <button
                  key={p.product_id}
                  type="button"
                  className={`hero-spotlight-dot${i === index ? ' active' : ''}`}
                  onClick={() => setIndex(i)}
                  aria-label={`Show ${p.name}`}
                  aria-current={i === index ? 'true' : undefined}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
