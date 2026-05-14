import { useState } from 'react';
import { getCategorySwatch } from '../utils/categorySwatch';

interface ProductThumbProps {
  imageUrl?: string | null;
  category: string;
  alt: string;
  className?: string;
  style?: React.CSSProperties;
  emojiSize?: number;
}

export function ProductThumb({
  imageUrl,
  category,
  alt,
  className,
  style,
  emojiSize = 36,
}: ProductThumbProps) {
  const [failed, setFailed] = useState(false);
  const swatch = getCategorySwatch(category);
  const showImage = Boolean(imageUrl) && !failed;

  return (
    <div
      className={className}
      style={{
        position: 'relative',
        overflow: 'hidden',
        background: swatch.gradient,
        display: 'grid',
        placeItems: 'center',
        ...style,
      }}
    >
      {showImage ? (
        <img
          src={imageUrl!}
          alt={alt}
          loading="lazy"
          referrerPolicy="no-referrer"
          style={{
            position: 'absolute',
            inset: 0,
            width: '100%',
            height: '100%',
            objectFit: 'cover',
          }}
          onError={() => setFailed(true)}
        />
      ) : (
        <span className="product-emoji" style={{ fontSize: emojiSize }}>
          {swatch.emoji}
        </span>
      )}
    </div>
  );
}
