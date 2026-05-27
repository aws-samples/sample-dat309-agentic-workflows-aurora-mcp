import { TripArt, type TripArtVariant } from './TripArt';

interface MobileTrip {
  title: string;
  dates: string;
  price: string;
  art: TripArtVariant;
  trend?: string;
}

const mobileTrips: MobileTrip[] = [
  {
    title: 'Willamette Valley, Oregon',
    dates: 'Nov 7 - 10, 3 nights',
    price: 'From $1,950',
    art: 'willamette',
    trend: 'Trending',
  },
  {
    title: 'Napa Valley, California',
    dates: 'Nov 14 - 17, 3 nights',
    price: 'From $2,450',
    art: 'napa',
  },
];

const bottomNav = ['Concierge', 'Trips', 'Discover', 'Messages', 'Profile'];

function Avatar() {
  return <span className="mds-avatar" aria-hidden="true" />;
}

function MobileTripCard({ trip, hero = false }: { trip: MobileTrip; hero?: boolean }) {
  return (
    <article className={`mds-mobile-trip${hero ? ' is-hero' : ''}`}>
      <TripArt variant={trip.art} mobile />
      <div className="mds-mobile-trip-copy">
        {trip.trend && <span className="mds-trend">{trip.trend}</span>}
        <strong>{trip.title}</strong>
        <span>
          {trip.dates}
          <br />
          {trip.price}
        </span>
        <span className="mds-chev" aria-hidden="true" />
      </div>
    </article>
  );
}

export function MobileMeridianApp() {
  return (
    <>
      <div className="mds-dynamic-island" />
      <div className="mds-phone-status">
        <span>9:41</span>
        <span>5G</span>
      </div>

      <div className="mds-phone-app">
        <div className="mds-phone-top">
          <span className="mds-hamburger" aria-hidden="true" />
          <div className="mds-phone-title">Meridian</div>
          <span className="mds-bell" aria-hidden="true" />
        </div>

        <div className="mds-mobile-profile">
          <Avatar />
          <div>
            <strong>Alex Morgan</strong>
            <span>Explorer</span>
          </div>
          <button className="mds-profile-button" type="button">
            View profile
          </button>
        </div>

        <div className="mds-mobile-user-bubble">
          I'm looking for a long weekend in wine country in November. Boutique,
          walkable towns, great food, and relaxing spa options.
        </div>

        <div className="mds-mobile-copy">
          Here are a few recommendations I think you'll love.
        </div>

        <div className="mds-mobile-cards">
          {mobileTrips.map((trip, index) => (
            <MobileTripCard trip={trip} hero={index === 0} key={trip.title} />
          ))}
        </div>

        <div className="mds-mobile-composer">
          <span>Ask Meridian anything...</span>
          <span className="mds-mic" aria-hidden="true" />
        </div>

        <nav className="mds-bottom-nav" aria-label="Mobile navigation">
          {bottomNav.map((item, index) => (
            <div className={index === 0 ? 'is-active' : ''} key={item}>
              <span className="mds-nav-dot" aria-hidden="true" />
              {item}
            </div>
          ))}
        </nav>
      </div>
    </>
  );
}
