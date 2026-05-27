import { LaptopFrame } from './LaptopFrame';
import { PhoneFrame } from './PhoneFrame';
import './meridianShowcase.css';

export function MeridianDeviceShowcase() {
  return (
    <main
      className="mds-root"
      aria-label="Cinematic Meridian app showcase with laptop and mobile app side by side"
    >
      <div className="mds-stage">
        <div className="mds-grain" />
        <div className="mds-ambient-line" />
        <div className="mds-reflection-laptop" />
        <div className="mds-reflection-phone" />

        <section className="mds-device-row" aria-label="Meridian device showcase">
          <LaptopFrame />
          <PhoneFrame />
        </section>
      </div>
    </main>
  );
}

export default MeridianDeviceShowcase;
