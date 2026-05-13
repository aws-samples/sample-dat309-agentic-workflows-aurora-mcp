/**
 * ProductsSection — Daylight Studio product grid with image + swatch fallback
 */
import { useState, useEffect } from 'react';
import { FadeIn } from '../components/FadeIn';
import { fetchProducts } from '../api/client';
import type { Product } from '../types';
import { ProductThumb } from '../components/ProductThumb';

export function ProductsSection() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProducts(undefined, 8, true)
      .then(setProducts)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <section
      id="products"
      style={{
        padding: '0 28px 56px',
        maxWidth: 1180,
        margin: '0 auto',
      }}
    >
      <FadeIn>
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-end',
            marginBottom: 24,
            paddingTop: 32,
            borderTop: '1px solid var(--dl-line)',
          }}
        >
          <h2 className="section-headline" style={{ margin: 0 }}>
            Featured trips
          </h2>
          <div style={{ fontSize: 13, color: 'var(--dl-muted)' }}>
            Showing <b style={{ color: 'var(--dl-ink)' }}>6 trip types</b> · sorted by{' '}
            <b style={{ color: 'var(--dl-ink)' }}>Relevance</b>
          </div>
        </div>
      </FadeIn>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
          gap: 14,
        }}
      >
        {loading
          ? Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="product-card" style={{ opacity: 0.5 }}>
                <div className="product-card-image" style={{ background: 'var(--dl-grid-bg)' }} />
                <div style={{ height: 14, background: 'var(--dl-grid-bg)', borderRadius: 4 }} />
              </div>
            ))
          : products.map((p, i) => (
              <FadeIn key={p.product_id} delay={i * 0.06}>
                <div className="product-card">
                  <ProductThumb
                    imageUrl={p.image_url}
                    category={p.category}
                    alt={p.name}
                    className="product-card-image"
                  />
                  <div className="product-name">{p.name}</div>
                  <div className="product-tagline">
                    {p.brand} · {p.category}
                  </div>
                  <div className="product-footer">
                    <span className="product-price">${p.price.toFixed(0)}</span>
                    <button className="product-add-btn" aria-label="Add to cart">
                      +
                    </button>
                  </div>
                </div>
              </FadeIn>
            ))}
      </div>

      <FadeIn delay={0.2}>
        <div className="embedding-snippet">
          <div className="embedding-code">
            <span style={{ color: 'var(--dl-muted)' }}>embedding</span>
            <span> = </span>
            <span style={{ color: 'var(--dl-sky)' }}>cohere_embed</span>
            <span>(</span>
            <span style={{ color: 'var(--dl-leaf)' }}>&quot;weekend in Tokyo with great food&quot;</span>
            <span>) → </span>
            <span style={{ color: 'var(--dl-accent)' }}>[0.0234, -0.0891, … ×1024]</span>
          </div>
        </div>
      </FadeIn>
    </section>
  );
}
