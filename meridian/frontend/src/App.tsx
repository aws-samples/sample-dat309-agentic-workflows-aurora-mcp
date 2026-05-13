/**
 * Meridian — Daylight Studio single-page application
 */
import { useScrollY } from './hooks/useScrollY';
import { StickyNav } from './components/StickyNav';
import { HeroSection } from './sections/HeroSection';
import { ProductsSection } from './sections/ProductsSection';
import { HowItWorksSection } from './sections/HowItWorksSection';
import { Vision2026Section } from './sections/Vision2026Section';
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
      <Vision2026Section />
      <AgentSection />
      <Footer />
    </div>
  );
}
