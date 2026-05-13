/**
 * Meridian — Daylight Studio single-page application
 */
import { useScrollY } from './hooks/useScrollY';
import { StickyNav } from './components/StickyNav';
import { HeroSection } from './sections/HeroSection';
import { ProductsSection } from './sections/ProductsSection';
import { HowItWorksSection } from './sections/HowItWorksSection';
import { AgentSection } from './sections/AgentSection';
import { Footer } from './components/Footer';

export default function App() {
  const scrollY = useScrollY();

  return (
    <div style={{ background: 'var(--dl-bg)', minHeight: '100vh' }}>
      <StickyNav scrollY={scrollY} />
      <HeroSection scrollY={scrollY} />
      <ProductsSection />
      <HowItWorksSection />
      <AgentSection />
      <Footer />
    </div>
  );
}
