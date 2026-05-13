const CATEGORY_SWATCHES: Record<string, { gradient: string; emoji: string }> = {
  'Running Shoes': { gradient: 'linear-gradient(135deg, #ffd9c2, #ffb38a)', emoji: '👟' },
  'Training Shoes': { gradient: 'linear-gradient(135deg, #ffc9a8, #ff9f6b)', emoji: '👟' },
  'Fitness Equipment': { gradient: 'linear-gradient(135deg, #cfe7ff, #9bc7f5)', emoji: '🏋️' },
  Apparel: { gradient: 'linear-gradient(135deg, #f0e6d8, #d4c4a8)', emoji: '👕' },
  Accessories: { gradient: 'linear-gradient(135deg, #dde2d3, #bcc5a9)', emoji: '⌚' },
  Recovery: { gradient: 'linear-gradient(135deg, #e7e2f5, #c8bfe6)', emoji: '🧘' },
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
  if (lower.includes('running') || lower.includes('training') || lower.includes('shoe')) {
    return CATEGORY_SWATCHES['Running Shoes'];
  }
  if (lower.includes('equipment') || lower.includes('strength')) {
    return CATEGORY_SWATCHES['Fitness Equipment'];
  }
  if (lower.includes('apparel') || lower.includes('wear')) {
    return CATEGORY_SWATCHES.Apparel;
  }
  if (lower.includes('accessor') || lower.includes('watch')) {
    return CATEGORY_SWATCHES.Accessories;
  }
  if (lower.includes('recover')) {
    return CATEGORY_SWATCHES.Recovery;
  }

  return DEFAULT_SWATCH;
}
