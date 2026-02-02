/**
 * Custom hook for tracking scroll position
 * Used for parallax effects and scroll-triggered animations
 */
import { useState, useEffect } from 'react';

export function useScrollY(): number {
  const [y, setY] = useState(0);

  useEffect(() => {
    const handleScroll = () => setY(window.scrollY);
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return y;
}
