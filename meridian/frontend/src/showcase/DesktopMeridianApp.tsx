import { TripArt, type TripArtVariant } from './TripArt';

interface TripRecommendation {
  title: string;
  dates: string;
  price: string;
  art: TripArtVariant;
}

interface DesktopNavItem {
  label: string;
  icon: string;
  active?: boolean;
  badge?: string;
}

const desktopTrips: TripRecommendation[] = [
  {
    title: 'Willamette Valley, Oregon',
    dates: 'Nov 7 - 10',
    price: 'From $1,950',
    art: 'willamette',
  },
  {
    title: 'Napa Valley, California',
    dates: 'Nov 14 - 17',
    price: 'From $2,450',
    art: 'napa',
  },
  {
    title: 'Mendoza, Argentina',
    dates: 'Nov 21 - 24',
    price: 'From $1,850',
    art: 'mendoza',
  },
];

const navItems: DesktopNavItem[] = [
  { label: 'Concierge', icon: 'bag', active: true },
  { label: 'Trips', icon: 'calendar' },
  { label: 'Discover', icon: 'pin' },
  { label: 'Profile', icon: 'user' },
  { label: 'Preferences', icon: 'gear' },
  { label: 'Messages', icon: 'message', badge: '2' },
];

const travelerFacts = [
  ['Profile', 'Explorer'],
  ['Travel style', 'Boutique, immersive, relaxed'],
  ['Interests', 'Wine, food, architecture, wellness'],
  ['Loyalty programs', 'Marriott Bonvoy, Delta SkyMiles'],
  ['Recent trips', 'Tuscany, Kyoto, Palm Springs'],
] as const;

const activityItems = [
  { label: 'Understanding your request', done: true },
  { label: 'Searching preference-matched destinations', done: true },
  { label: 'Checking availability and pricing', done: true },
  { label: 'Curating personalized recommendations', done: true },
  { label: 'Optimizing your itinerary', done: false },
] as const;

function BrandMark() {
  return <span className="mds-brand-mark" aria-hidden="true" />;
}

function Avatar() {
  return <span className="mds-avatar" aria-hidden="true" />;
}

function DesktopSidebar() {
  return (
    <aside className="mds-desktop-sidebar">
      <div className="mds-brand">
        <BrandMark />
        Meridian
      </div>

      <nav className="mds-nav-items" aria-label="Desktop navigation">
        {navItems.map((item) => (
          <div
            key={item.label}
            className={`mds-nav-item${item.active ? ' is-active' : ''}`}
          >
            <span
              className={`mds-nav-icon mds-nav-icon-${item.icon}`}
              data-badge={item.badge}
              aria-hidden="true"
            />
            {item.label}
          </div>
        ))}
      </nav>

      <div className="mds-sidebar-spacer" />

      <div className="mds-nav-item">
        <span className="mds-nav-icon mds-nav-icon-gear" aria-hidden="true" />
        Settings
      </div>

      <div className="mds-account-mini">
        <Avatar />
        <div className="mds-account-copy">
          <strong>Alex Morgan</strong>
          <span>Explorer</span>
        </div>
      </div>
    </aside>
  );
}

function DesktopTripCard({ trip }: { trip: TripRecommendation }) {
  return (
    <article className="mds-trip-card">
      <TripArt variant={trip.art} />
      <div className="mds-trip-body">
        <div className="mds-trip-title">{trip.title}</div>
        <div className="mds-trip-meta">{trip.dates}</div>
        <div className="mds-trip-price">
          <span>{trip.price}</span>
          <span className="mds-circle-arrow" aria-hidden="true" />
        </div>
      </div>
    </article>
  );
}

function TravelerContextPanel() {
  return (
    <section className="mds-info-panel">
      <div className="mds-panel-head">
        <strong>Traveler context</strong>
        <span>Edit</span>
      </div>

      <div className="mds-profile-line">
        <Avatar />
        <div>
          <strong>Alex Morgan</strong>
          <small>alex.morgan@gmail.com</small>
        </div>
      </div>

      <div className="mds-facts">
        {travelerFacts.map(([label, value]) => (
          <div className="mds-fact-row" key={label}>
            <span>{label}</span>
            <span>{value}</span>
          </div>
        ))}
      </div>

      <div className="mds-linkish">View all</div>
    </section>
  );
}

function ActivityPanel() {
  return (
    <section className="mds-info-panel mds-activity">
      <div className="mds-panel-head">
        <strong>Meridian activity</strong>
        <span className="mds-live-dot">Live</span>
      </div>

      {activityItems.map((item) => (
        <div className="mds-activity-item" key={item.label}>
          <span
            className={`mds-check${item.done ? '' : ' is-live'}`}
            aria-hidden="true"
          />
          <span>{item.label}</span>
        </div>
      ))}
    </section>
  );
}

export function DesktopMeridianApp() {
  return (
    <div className="mds-desktop-app">
      <DesktopSidebar />

      <main className="mds-desktop-main">
        <div className="mds-top-actions">
          <span>VIP</span>
          <span>USD</span>
          <span aria-hidden="true">...</span>
        </div>

        <h1>Good morning, Alex.</h1>
        <div className="mds-subhead">Where would you like to go next?</div>

        <div className="mds-chat-prompt">
          I'm looking for a long weekend in wine country in November. Boutique,
          walkable towns, great food, and relaxing spa options.
        </div>

        <div className="mds-assistant-line">
          Perfect. I've found a few places that match your style.
        </div>

        <div className="mds-rec-grid">
          {desktopTrips.map((trip) => (
            <DesktopTripCard trip={trip} key={trip.title} />
          ))}
        </div>

        <button className="mds-more-button" type="button">
          View more recommendations
        </button>

        <div className="mds-composer-desktop">
          <div className="mds-input-shell">
            <span>Ask Meridian anything...</span>
            <span className="mds-send-dot" aria-hidden="true" />
          </div>
          <div className="mds-quick-actions">
            <span>Add travelers</span>
            <span>Change dates</span>
            <span>Add spa</span>
            <span>Direct flights</span>
          </div>
        </div>
      </main>

      <aside className="mds-desktop-right">
        <TravelerContextPanel />
        <ActivityPanel />
      </aside>
    </div>
  );
}
