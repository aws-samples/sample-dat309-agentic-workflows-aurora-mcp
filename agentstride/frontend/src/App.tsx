/**
 * AgentStride - Apple-style parallax scrolling single-page application
 * Features: Hero, Products, How It Works, Agent Chat sections
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
    <div style={{ background: '#060a14', minHeight: '100vh' }}>
      <StickyNav scrollY={scrollY} />
      <HeroSection scrollY={scrollY} />
      <ProductsSection />
      <HowItWorksSection />
      <AgentSection />
      <Footer />
    </div>
  );
}
