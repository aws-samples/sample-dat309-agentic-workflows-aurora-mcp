const CATEGORY_SWATCHES: Record<string, { gradient: string; emoji: string }> = {
  'City Breaks': { gradient: 'linear-gradient(135deg, #cfe7ff, #9bc7f5)', emoji: '🏙️' },
  'Beach & Resort': { gradient: 'linear-gradient(135deg, #ffd9c2, #ffb38a)', emoji: '🏖️' },
  'Adventure & Outdoors': { gradient: 'linear-gradient(135deg, #dde2d3, #bcc5a9)', emoji: '🏔️' },
  'Wellness & Luxury': { gradient: 'linear-gradient(135deg, #e7e2f5, #c8bfe6)', emoji: '🧘' },
  'Family Trips': { gradient: 'linear-gradient(135deg, #f0e6d8, #d4c4a8)', emoji: '👨‍👩‍👧' },
  'Business Travel': { gradient: 'linear-gradient(135deg, #eef0e9, #c5cdd8)', emoji: '✈️' },
};

const DEFAULT_SWATCH = {
  gradient: 'linear-gradient(135deg, #eef0e9, #dde2d3)',
  emoji: '✦',
};

export function getCategorySwatch(category: string) {
  if (CATEGORY_SWATCHES[category]) {
    return CATEGORY_SWATCHES[category];
  }

  const lower = category.toLowerCase();
  if (lower.includes('city') || lower.includes('urban')) {
    return CATEGORY_SWATCHES['City Breaks'];
  }
  if (lower.includes('beach') || lower.includes('resort') || lower.includes('island')) {
    return CATEGORY_SWATCHES['Beach & Resort'];
  }
  if (lower.includes('adventure') || lower.includes('outdoor') || lower.includes('trek')) {
    return CATEGORY_SWATCHES['Adventure & Outdoors'];
  }
  if (lower.includes('wellness') || lower.includes('luxury') || lower.includes('spa')) {
    return CATEGORY_SWATCHES['Wellness & Luxury'];
  }
  if (lower.includes('family') || lower.includes('kids')) {
    return CATEGORY_SWATCHES['Family Trips'];
  }
  if (lower.includes('business') || lower.includes('conference')) {
    return CATEGORY_SWATCHES['Business Travel'];
  }

  return DEFAULT_SWATCH;
}
