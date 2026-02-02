/**
 * HeroSection - Full viewport hero with parallax layers
 * Features gradient background with rotating product imagery
 */
import { useState, useEffect } from 'react';
import { ParallaxLayer } from '../components/ParallaxLayer';

interface HeroSectionProps {
  scrollY: number;
}

// Rotating background images - fitness/athletic themed
const backgroundImages = [
  'https://images.unsplash.com/photo-1571902943202-507ec2618e8f?w=1920&q=80', // Gym/fitness center
  'https://images.unsplash.com/photo-1461896836934- voices-of-the-world?w=1920&q=80', // Running track
  'https://images.unsplash.com/photo-1476480862126-209bfaa8edc8?w=1920&q=80', // Runner on road
  'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=1920&q=80', // Weights/gym
  'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=1920&q=80', // Modern gym
];

export function HeroSection({ scrollY }: HeroSectionProps) {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [isTransitioning, setIsTransitioning] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setIsTransitioning(true);
      setTimeout(() => {
        setCurrentImageIndex((prev) => (prev + 1) % backgroundImages.length);
        setIsTransitioning(false);
      }, 500); // Half of transition duration
    }, 6000); // Change every 6 seconds

    return () => clearInterval(interval);
  }, []);

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

      {/* Rotating product background images - fitness/athletic theme */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          backgroundImage: `url(${backgroundImages[currentImageIndex]})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          opacity: isTransitioning ? 0.06 : 0.12,
          filter: `blur(${2 + blur * 0.5}px)`,
          transform: `scale(${1.1 + scrollY * 0.0002})`,
          transition: 'opacity 1s ease-in-out, background-image 0.5s ease-in-out',
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
            color: '#ffffff',
          }}
        >
          AgentStride
        </h1>

        {/* Tagline */}
        <p
          style={{
            fontSize: 28,
            fontWeight: 600,
            color: 'rgba(248,250,252,0.95)',
            marginBottom: 12,
            fontFamily: "'SF Pro Display', -apple-system, sans-serif",
            letterSpacing: '0.02em',
          }}
        >
          Ask. Shop. Done.
        </p>

        {/* Subtitle */}
        <p
          style={{
            fontSize: 18,
            color: 'rgba(226,232,240,0.85)',
            lineHeight: 1.6,
            maxWidth: 400,
            margin: '0 auto 40px',
            fontFamily: "'SF Pro Text', -apple-system, sans-serif",
          }}
        >
          Shopping, powered by agents.
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
