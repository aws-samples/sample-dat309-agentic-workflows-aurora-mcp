/**
 * ParallaxLayer component for creating depth effects on scroll
 * Speed controls how fast the layer moves relative to scroll
 */
import { ReactNode, CSSProperties } from 'react';

interface ParallaxLayerProps {
  children: ReactNode;
  speed?: number;
  scrollY: number;
  style?: CSSProperties;
}

export function ParallaxLayer({ children, speed = 0.5, scrollY, style = {} }: ParallaxLayerProps) {
  return (
    <div
      style={{
        ...style,
        transform: `translateY(${scrollY * speed}px)`,
        willChange: 'transform',
      }}
    >
      {children}
    </div>
  );
}
