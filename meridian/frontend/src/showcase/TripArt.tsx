export type TripArtVariant = 'willamette' | 'napa' | 'mendoza';

interface TripArtProps {
  variant: TripArtVariant;
  mobile?: boolean;
  className?: string;
}

export function TripArt({ variant, mobile = false, className = '' }: TripArtProps) {
  const classes = [
    'mds-trip-art',
    mobile ? 'mds-mobile-art' : '',
    `mds-art-${variant}`,
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return <div className={classes} aria-hidden="true" />;
}
