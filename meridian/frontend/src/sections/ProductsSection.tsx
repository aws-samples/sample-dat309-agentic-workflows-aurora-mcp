/**
 * ProductsSection — Meridian Pro refined trip catalog
 *
 * 4-up grid with category-tinted hero, real cover images when available,
 * and a "match because" tag set derived from category.
 */
import { useEffect, useMemo, useState } from 'react';
import { FadeIn } from '../components/FadeIn';
import { useAgentBridge } from '../context/AgentBridge';
import { fetchProducts } from '../api/client';
import type { Product } from '../types';

const TAGS_BY_CATEGORY: Record<string, string[]> = {
  'City Breaks': ['Walkable', 'Refundable'],
  'Beach & Resort': ['Coastal', 'Adults only'],
  'Adventure & Outdoors': ['Hiking', 'Refundable'],
  'Wellness & Luxury': ['Spa', 'Slow pace'],
  'Business travel': ['Lounge access', '1-stop'],
};

function moneyFormat(price: number): string {
  return `$${price.toFixed(0)}`;
}

type SortMode = 'relevance' | 'price-asc' | 'price-desc';

export function ProductsSection() {
  const { openConcierge } = useAgentBridge();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [category, setCategory] = useState<string>('all');
  const [sort, setSort] = useState<SortMode>('relevance');
  const [saved, setSaved] = useState<Set<string>>(new Set());

  useEffect(() => {
    setLoading(true);
    fetchProducts(undefined, 12, true)
      .then((items) => {
        setProducts(items);
        setError(null);
      })
      .catch(() => {
        setError('Backend offline — start FastAPI on localhost:8000 to load live trips.');
      })
      .finally(() => setLoading(false));
  }, []);

  const categories = useMemo(() => {
    const cats = new Set(products.map((p) => p.category));
    return ['all', ...Array.from(cats).sort()];
  }, [products]);

  const visible = useMemo(() => {
    let list = category === 'all' ? products : products.filter((p) => p.category === category);
    if (sort === 'price-asc') list = [...list].sort((a, b) => a.price - b.price);
    if (sort === 'price-desc') list = [...list].sort((a, b) => b.price - a.price);
    return list;
  }, [products, category, sort]);

  const askAboutTrip = (p: Product) => {
    openConcierge({
      phase: 4,
      prompt: `Tell me about ${p.name} for two travelers — dates, pricing, and why it fits our profile.`,
      send: true,
    });
  };

  return (
    <section id="products" className="mp-section">
      <FadeIn>
        <div className="mp-section-h-row">
          <div className="mp-section-h">
            <div className="mp-label-row">Trip catalog · live from Aurora</div>
            <h2>
              Curated trips, <em className="serif">embedded</em>.
            </h2>
            <p>
              30 hand-curated packages indexed with Cohere Embed v4 (1024d) and a tsvector for
              lexical fallback. The concierge searches across both — and writes a <em>match because</em>{' '}
              sentence for every result.
            </p>
          </div>
          <div className="actions">
            <select
              className="mp-btn ghost sm mp-select"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              aria-label="Filter by category"
            >
              {categories.map((c) => (
                <option key={c} value={c}>
                  {c === 'all' ? 'All categories' : c}
                </option>
              ))}
            </select>
            <select
              className="mp-btn ghost sm mp-select"
              value={sort}
              onChange={(e) => setSort(e.target.value as SortMode)}
              aria-label="Sort trips"
            >
              <option value="relevance">Sorted: relevance</option>
              <option value="price-asc">Price: low → high</option>
              <option value="price-desc">Price: high → low</option>
            </select>
          </div>
        </div>
      </FadeIn>

      {error && (
        <div
          style={{
            margin: '0 0 16px',
            padding: '10px 14px',
            background: 'rgba(255,91,31,0.06)',
            border: '1px solid rgba(255,91,31,0.25)',
            borderRadius: 12,
            color: 'var(--mp-accent-2)',
            fontSize: 13,
          }}
        >
          {error}
        </div>
      )}

      <div className="mp-pkg-grid">
        {loading
          ? Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="mp-pkg" style={{ opacity: 0.4 }}>
                <div className="mp-pkg-hero" />
                <div className="mp-pkg-body">
                  <div style={{ height: 14, background: 'var(--mp-rail)', borderRadius: 4 }} />
                  <div
                    style={{
                      height: 10,
                      background: 'var(--mp-rail)',
                      borderRadius: 4,
                      width: '60%',
                      marginTop: 8,
                    }}
                  />
                </div>
              </div>
            ))
          : visible.map((p, i) => {
              const tags = TAGS_BY_CATEGORY[p.category] ?? ['Refundable'];
              return (
                <FadeIn key={p.product_id} delay={i * 0.04}>
                  <article className="mp-pkg">
                    <div className="mp-pkg-hero" data-cat={p.category}>
                      {p.image_url && <img src={p.image_url} alt={p.name} />}
                      <span className="mp-pkg-cat">{p.category}</span>
                      <button
                        type="button"
                        className={`mp-pkg-save${saved.has(p.product_id) ? ' saved' : ''}`}
                        aria-label={saved.has(p.product_id) ? 'Saved' : 'Save'}
                        onClick={() =>
                          setSaved((prev) => {
                            const next = new Set(prev);
                            if (next.has(p.product_id)) next.delete(p.product_id);
                            else next.add(p.product_id);
                            return next;
                          })
                        }
                      >
                        {saved.has(p.product_id) ? '♥' : '♡'}
                      </button>
                    </div>
                    <div className="mp-pkg-body">
                      <div className="mp-pkg-name">{p.name}</div>
                      <div className="mp-pkg-where">
                        {p.brand}
                        {p.description ? ` · ${p.description.slice(0, 38)}${p.description.length > 38 ? '…' : ''}` : ''}
                      </div>
                      <div className="mp-pkg-tags">
                        {tags.map((t) => (
                          <span key={t}>{t}</span>
                        ))}
                      </div>
                      <div className="mp-pkg-foot">
                        <div className="mp-pkg-price">
                          {moneyFormat(p.price)} <small>/ pair</small>
                        </div>
                        <button
                          type="button"
                          className="mp-pkg-add"
                          aria-label="Ask concierge about this trip"
                          onClick={() => askAboutTrip(p)}
                        >
                          +
                        </button>
                      </div>
                    </div>
                  </article>
                </FadeIn>
              );
            })}
      </div>
    </section>
  );
}
