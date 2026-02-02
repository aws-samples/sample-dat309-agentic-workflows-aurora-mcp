/**
 * ProductsSection - Product catalog with scroll-triggered grid
 * Features staggered animations and embedding code snippet
 */
import { useState, useEffect } from 'react';
import { FadeIn } from '../components/FadeIn';
import { fetchProducts } from '../api/client';
import type { Product } from '../types';

export function ProductsSection() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch one featured product per category (6 categories)
    fetchProducts(undefined, 6, true)
      .then(setProducts)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <section
      id="products"
      style={{
        position: 'relative',
        padding: '120px 40px 100px',
        background: '#060a14',
        overflow: 'hidden',
      }}
    >
      {/* Top accent line */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: 1,
          background: 'linear-gradient(90deg, transparent, rgba(59,130,246,0.3), transparent)',
        }}
      />

      <div style={{ maxWidth: 1200, margin: '0 auto' }}>
        {/* Header */}
        <FadeIn>
          <div style={{ textAlign: 'center', marginBottom: 80 }}>
            <span className="section-label" style={{ color: '#3b82f6' }}>
              Product Catalog
            </span>
            <h2 className="section-headline">Every product, one search away.</h2>
            <p className="section-subtitle">
              30 products across 6 categories. Each embedded as a 1024-dimensional vector using Nova
              Multimodal — searchable by text or image.
            </p>
          </div>
        </FadeIn>

        {/* Product grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: 24,
          }}
        >
          {loading ? (
            Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="product-card" style={{ opacity: 0.5 }}>
                <div className="product-card-image" style={{ background: '#1e293b' }} />
                <div style={{ padding: '20px 24px 24px' }}>
                  <div style={{ height: 20, background: '#1e293b', borderRadius: 4, marginBottom: 8 }} />
                  <div style={{ height: 14, background: '#1e293b', borderRadius: 4, width: '60%' }} />
                </div>
              </div>
            ))
          ) : (
            products.map((p, i) => (
              <FadeIn key={p.product_id} delay={i * 0.1}>
                <div className="product-card">
                  {/* Product image area */}
                  <div className="product-card-image" style={{ position: 'relative' }}>
                    <img
                      src={p.image_url}
                      alt={p.name}
                      style={{
                        width: '100%',
                        height: '100%',
                        objectFit: 'cover',
                        position: 'absolute',
                        top: 0,
                        left: 0,
                      }}
                      onError={(e) => {
                        (e.target as HTMLImageElement).style.display = 'none';
                      }}
                    />
                    <div className="product-card-gradient" />
                    <div className="product-category-badge">{p.category}</div>
                  </div>

                  {/* Product info */}
                  <div style={{ padding: '20px 24px 24px' }}>
                    <h3 className="product-name">{p.name}</h3>
                    <p className="product-tagline">{p.brand}</p>
                    <div className="product-footer">
                      <span className="product-price">${p.price.toFixed(2)}</span>
                      <span className="product-stock in-stock">In Stock</span>
                    </div>
                  </div>
                </div>
              </FadeIn>
            ))
          )}
        </div>

        {/* Embedding code snippet */}
        <FadeIn delay={0.3}>
          <div className="embedding-snippet">
            <div className="embedding-code">
              <span style={{ color: '#94a3b8' }}>embedding</span>
              <span style={{ color: '#475569' }}> = </span>
              <span style={{ color: '#3b82f6' }}>nova_embed</span>
              <span style={{ color: '#475569' }}>(</span>
              <span style={{ color: '#10b981' }}>"comfortable running shoes"</span>
              <span style={{ color: '#475569' }}>)</span>
              <span style={{ color: '#334155' }}> → </span>
              <span style={{ color: '#f59e0b' }}>[0.0234, -0.0891, 0.1247, ... </span>
              <span style={{ color: '#475569' }}>×1024 dimensions</span>
              <span style={{ color: '#f59e0b' }}>]</span>
            </div>
          </div>
        </FadeIn>
      </div>
    </section>
  );
}
