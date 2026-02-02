/**
 * HeroSection - Full viewport hero with parallax layers
 * Features gradient background with realistic product imagery
 */
import { ParallaxLayer } from '../components/ParallaxLayer';

interface HeroSectionProps {
  scrollY: number;
}

export function HeroSection({ scrollY }: HeroSectionProps) {
  const opacity = Math.max(0, 1 - scrollY / 600);
  const scale = 1 + scrollY * 0.0003;
  const blur = Math.min(scrollY / 100, 10);

  return (
    <section
      style={{
        position: 'relative',
        height: '100vh',
        overflow: 'hidden',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      {/* Base gradient background */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'radial-gradient(ellipse 80% 60% at 50% 40%, #0c1222, #060a14)',
        }}
      />

      {/* Realistic product background image - fitness/athletic theme */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          backgroundImage: 'url(https://images.unsplash.com/photo-1571902943202-507ec2618e8f?w=1920&q=80)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          opacity: 0.12,
          filter: `blur(${2 + blur * 0.5}px)`,
          transform: `scale(${1.1 + scrollY * 0.0002})`,
        }}
      />

      {/* Gradient orbs with parallax */}
      <ParallaxLayer scrollY={scrollY} speed={-0.15} style={{ position: 'absolute', inset: 0 }}>
        <div
          style={{
            position: 'absolute',
            top: '15%',
            left: '10%',
            width: 500,
            height: 500,
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(59,130,246,0.1), transparent 70%)',
            filter: `blur(${blur}px)`,
          }}
        />
        <div
          style={{
            position: 'absolute',
            top: '30%',
            right: '5%',
            width: 400,
            height: 400,
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(168,85,247,0.08), transparent 70%)',
            filter: `blur(${blur}px)`,
          }}
        />
      </ParallaxLayer>

      {/* Subtle grid overlay */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          opacity: 0.02,
          backgroundImage:
            'linear-gradient(rgba(255,255,255,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.3) 1px, transparent 1px)',
          backgroundSize: '80px 80px',
          transform: `translateY(${scrollY * -0.05}px)`,
        }}
      />

      {/* Hero content */}
      <div
        style={{
          position: 'relative',
          zIndex: 10,
          textAlign: 'center',
          opacity,
          transform: `scale(${scale})`,
          filter: `blur(${blur * 0.3}px)`,
          maxWidth: 900,
          padding: '0 24px',
        }}
      >
        {/* Tech stack breadcrumb */}
        <div
          style={{
            fontSize: 12,
            fontWeight: 600,
            letterSpacing: '0.2em',
            textTransform: 'uppercase',
            color: 'rgba(148,163,184,0.7)',
            marginBottom: 24,
            fontFamily: "'SF Mono', 'Fira Code', monospace",
          }}
        >
          Aurora PostgreSQL · MCP · pgvector · Nova Multimodal
        </div>

        {/* Headline with shimmer */}
        <h1
          className="hero-headline"
          style={{
            fontSize: 'clamp(48px, 8vw, 88px)',
            fontWeight: 700,
            lineHeight: 1.05,
            letterSpacing: '-0.04em',
            margin: '0 0 24px',
            fontFamily: "'SF Pro Display', -apple-system, sans-serif",
            background: 'linear-gradient(135deg, #f8fafc 0%, #94a3b8 50%, #f8fafc 100%)',
            backgroundSize: '200% 200%',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            animation: 'shimmer 6s ease-in-out infinite',
          }}
        >
          ClickShop
        </h1>

        {/* Tagline */}
        <p
          style={{
            fontSize: 24,
            fontWeight: 500,
            color: 'rgba(248,250,252,0.9)',
            marginBottom: 16,
            fontFamily: "'SF Pro Display', -apple-system, sans-serif",
          }}
        >
          Search smarter. Shop faster.
        </p>

        {/* Subtitle */}
        <p
          style={{
            fontSize: 17,
            color: 'rgba(148,163,184,0.8)',
            lineHeight: 1.7,
            maxWidth: 560,
            margin: '0 auto 40px',
            fontFamily: "'SF Pro Text', -apple-system, sans-serif",
          }}
        >
          An AI-powered shopping experience that understands what you're looking for — 
          using semantic search, multimodal embeddings, and intelligent agents.
        </p>

        {/* CTA buttons */}
        <div style={{ display: 'flex', gap: 16, justifyContent: 'center' }}>
          <button
            onClick={() => document.getElementById('products')?.scrollIntoView({ behavior: 'smooth' })}
            className="hero-btn-primary"
          >
            Explore Products
          </button>
          <button
            onClick={() => document.getElementById('agent')?.scrollIntoView({ behavior: 'smooth' })}
            className="hero-btn-secondary"
          >
            Try the Agent
          </button>
        </div>
      </div>

      {/* Scroll indicator */}
      <div
        style={{
          position: 'absolute',
          bottom: 40,
          left: '50%',
          transform: 'translateX(-50%)',
          opacity: Math.max(0, 1 - scrollY / 200),
          animation: 'float 2.5s ease-in-out infinite',
        }}
      >
        <div
          style={{
            width: 24,
            height: 40,
            borderRadius: 12,
            border: '2px solid rgba(255,255,255,0.2)',
            display: 'flex',
            justifyContent: 'center',
            paddingTop: 8,
          }}
        >
          <div
            style={{
              width: 3,
              height: 8,
              borderRadius: 2,
              background: 'rgba(255,255,255,0.4)',
              animation: 'scrollDot 2s ease-in-out infinite',
            }}
          />
        </div>
      </div>
    </section>
  );
}
