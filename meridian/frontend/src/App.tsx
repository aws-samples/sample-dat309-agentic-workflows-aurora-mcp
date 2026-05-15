/**
 * Meridian Pro — light, professional single-page application.
 *
 * Section order is intentional: hero → journey → workspace → memory → trips → system → vision.
 * The agent workspace is the centerpiece; everything else supports it.
 */
import { AgentBridgeProvider } from './context/AgentBridge';
import { useScrollY } from './hooks/useScrollY';
import { StickyNav } from './components/StickyNav';
import { HeroSection } from './sections/HeroSection';
import { HowItWorksSection } from './sections/HowItWorksSection';
import { AgentSection } from './sections/AgentSection';
import { MemorySection } from './sections/MemorySection';
import { ProductsSection } from './sections/ProductsSection';
import { SystemSection } from './sections/SystemSection';
import { Vision2026Section } from './sections/Vision2026Section';
import { Footer } from './components/Footer';

export default function App() {
  const scrollY = useScrollY();

  return (
    <AgentBridgeProvider>
      <div style={{ background: 'var(--mp-bg)', minHeight: '100vh' }}>
        <StickyNav scrollY={scrollY} />
        <HeroSection scrollY={scrollY} />
        <HowItWorksSection />
        <AgentSection />
        <MemorySection />
        <ProductsSection />
        <SystemSection />
        <Vision2026Section />
        <Footer />
      </div>
    </AgentBridgeProvider>
  );
}
