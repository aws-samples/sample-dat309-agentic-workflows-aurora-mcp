/**
 * FadeIn component for scroll-triggered reveal animations
 * Supports multiple directions and configurable delays
 */
import { ReactNode } from 'react';
import { useInView } from '../hooks/useInView';

interface FadeInProps {
  children: ReactNode;
  delay?: number;
  direction?: 'up' | 'down' | 'left' | 'right' | 'none';
  className?: string;
}

const transforms: Record<string, string> = {
  up: 'translateY(60px)',
  down: 'translateY(-60px)',
  left: 'translateX(60px)',
  right: 'translateX(-60px)',
  none: 'none',
};

export function FadeIn({ children, delay = 0, direction = 'up', className = '' }: FadeInProps) {
  const [ref, visible] = useInView(0.1);

  return (
    <div
      ref={ref}
      className={className}
      style={{
        opacity: visible ? 1 : 0,
        transform: visible ? 'none' : transforms[direction],
        transition: `all 0.9s cubic-bezier(0.16,1,0.3,1) ${delay}s`,
      }}
    >
      {children}
    </div>
  );
}
