/**
 * HeroSection — Daylight Studio editorial hero with featured trip card
 */
import { useState, useEffect } from 'react';
import { fetchProducts } from '../api/client';
import type { Product } from '../types';
import { ProductThumb } from '../components/ProductThumb';

interface HeroSectionProps {
  scrollY: number;
}

export function HeroSection({ scrollY: _scrollY }: HeroSectionProps) {
  const [featured, setFeatured] = useState<Product | null>(null);

  useEffect(() => {
    fetchProducts(undefined, 1, true)
      .then((items) => setFeatured(items[0] ?? null))
      .catch(() => {});
  }, []);

  return (
    <section
      style={{
        padding: '100px 28px 56px',
        maxWidth: 1180,
        margin: '0 auto',
      }}
    >
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1.1fr 1fr',
          gap: 40,
          alignItems: 'center',
        }}
        className="hero-grid"
      >
        <div>
          <div className="dl-eyebrow">Travel, powered by agents</div>
          <h1 className="dl-display">
            Plan.
            <br />
            <em className="serif">Go.</em>
            <br />
            Done.
          </h1>
          <p className="dl-lede" style={{ marginBottom: 16 }}>
            A concierge that understands what you actually mean. Built on Aurora, MCP, and Cohere
            embeddings — so &ldquo;romantic week in Europe under $3k&rdquo; returns the right city
            break, beach escape, and rail pass. Available dates included.
          </p>
          <p className="dl-lede" style={{ marginBottom: 28, fontSize: 15, color: 'var(--dl-dim)' }}>
            Next: contextual memory, AgentCore runtime, and replayable traces — see the 2026 roadmap below.
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
            <div className="dl-stat">
              <b>30</b>packages
            </div>
            <div className="dl-stat">
              <b>6</b>trip types
            </div>
            <div className="dl-stat">
              <b>1024d</b>vectors
            </div>
            <div className="dl-stat">
              <b>~340ms</b>p50 latency
            </div>
          </div>
        </div>

        <div className="dl-feature-card">
          <ProductThumb
            imageUrl={featured?.image_url}
            category={featured?.category ?? 'City Breaks'}
            alt={featured?.name ?? 'Paris Long Weekend'}
            className="dl-feature-swatch"
            emojiSize={48}
          />
          <div
            style={{
              padding: '16px 20px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <div>
              <strong style={{ fontSize: 15 }}>{featured?.name ?? 'Paris Long Weekend'}</strong>
              <div style={{ fontSize: 12, color: 'var(--dl-muted)', marginTop: 2 }}>
                {featured ? `${featured.brand} · ${featured.category}` : 'Air France Vacations · City Breaks'}
              </div>
            </div>
            <div style={{ fontSize: 18, fontWeight: 700 }}>
              ${featured?.price.toFixed(0) ?? '1899'}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
