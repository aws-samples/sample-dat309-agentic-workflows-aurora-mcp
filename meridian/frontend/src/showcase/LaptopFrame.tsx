import { DesktopMeridianApp } from './DesktopMeridianApp';

export function LaptopFrame() {
  return (
    <div className="mds-laptop-wrap">
      <div className="mds-laptop" aria-label="MacBook style Meridian desktop app mockup">
        <div className="mds-laptop-lid">
          <div className="mds-laptop-screen">
            <div className="mds-screen-notch" />
            <DesktopMeridianApp />
          </div>
        </div>

        <div className="mds-laptop-base">
          <div className="mds-ports" aria-hidden="true">
            <span />
            <span />
            <span />
          </div>
        </div>
      </div>
    </div>
  );
}
