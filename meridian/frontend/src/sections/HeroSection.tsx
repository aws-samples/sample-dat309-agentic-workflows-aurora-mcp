/**
 * HeroSection — Daylight Studio editorial hero with featured product card
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
          <div className="dl-eyebrow">Shopping, powered by agents</div>
          <h1 className="dl-display">
            Ask.
            <br />
            <em className="serif">Shop.</em>
            <br />
            Done.
          </h1>
          <p className="dl-lede" style={{ marginBottom: 28 }}>
            An agent that understands what you actually mean. Built on Aurora, MCP, and Cohere
            embeddings — so &ldquo;something for marathon training&rdquo; returns the right shoe,
            watch, and recovery tool. In stock.
          </p>
          <div style={{ display: 'flex', gap: 10, marginBottom: 32 }}>
            <button
              onClick={() => document.getElementById('agent')?.scrollIntoView({ behavior: 'smooth' })}
              className="hero-btn-primary"
            >
              Talk to the agent
            </button>
            <button
              onClick={() => document.getElementById('products')?.scrollIntoView({ behavior: 'smooth' })}
              className="hero-btn-secondary"
            >
              See the catalog
            </button>
          </div>
          <div style={{ display: 'flex', gap: 28, flexWrap: 'wrap' }}>
            <div className="dl-stat">
              <b>30</b>products
            </div>
            <div className="dl-stat">
              <b>6</b>categories
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
            category={featured?.category ?? 'Running Shoes'}
            alt={featured?.name ?? 'Pegasus 41'}
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
              <strong style={{ fontSize: 15 }}>{featured?.name ?? 'Pegasus 41'}</strong>
              <div style={{ fontSize: 12, color: 'var(--dl-muted)', marginTop: 2 }}>
                {featured ? `${featured.brand} · ${featured.category}` : 'Nike · Running'}
              </div>
            </div>
            <div style={{ fontSize: 18, fontWeight: 700 }}>
              ${featured?.price.toFixed(0) ?? '140'}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
