/**
 * Product data for the ClickShop demo
 * 6 products displayed in the catalog section
 */
export interface Product {
  name: string;
  cat: string;
  price: number;
  rating: number;
  stock: number;
  sim: number;
  gradient: string;
  emoji: string;
  tagline: string;
}

export const PRODUCTS: Product[] = [
  {
    name: 'Nike Air Zoom Pegasus 41',
    cat: 'Running',
    price: 139.99,
    rating: 4.7,
    stock: 24,
    sim: 0.94,
    gradient: 'from-blue-500 to-cyan-400',
    emoji: '👟',
    tagline: 'Responsive cushioning for every mile',
  },
  {
    name: 'ASICS Gel-Nimbus 26',
    cat: 'Running',
    price: 159.99,
    rating: 4.8,
    stock: 12,
    sim: 0.91,
    gradient: 'from-red-500 to-orange-400',
    emoji: '👟',
    tagline: 'Premium gel technology for max comfort',
  },
  {
    name: 'Salomon Speedcross 6',
    cat: 'Trail',
    price: 139.99,
    rating: 4.6,
    stock: 31,
    sim: 0.87,
    gradient: 'from-emerald-500 to-teal-400',
    emoji: '🥾',
    tagline: 'Aggressive grip for technical terrain',
  },
  {
    name: 'Hoka Clifton 9',
    cat: 'Running',
    price: 144.99,
    rating: 4.5,
    stock: 8,
    sim: 0.84,
    gradient: 'from-amber-500 to-yellow-400',
    emoji: '👟',
    tagline: 'Ultra-light with maximum cushion',
  },
  {
    name: 'Brooks Ghost 16',
    cat: 'Running',
    price: 139.99,
    rating: 4.6,
    stock: 42,
    sim: 0.82,
    gradient: 'from-violet-500 to-purple-400',
    emoji: '👟',
    tagline: 'Smooth transitions, balanced feel',
  },
  {
    name: 'Garmin Forerunner 265',
    cat: 'Accessories',
    price: 349.99,
    rating: 4.9,
    stock: 15,
    sim: 0.79,
    gradient: 'from-slate-600 to-slate-400',
    emoji: '⌚',
    tagline: 'AMOLED display, advanced training metrics',
  },
];

export const ACTIVITIES = [
  { icon: '🤖', label: 'Reasoning', detail: "Analyzing: 'comfortable marathon shoes'", ms: 45, agent: 'Supervisor' },
  { icon: '🧠', label: 'Nova Embedding', detail: 'Text → 1024-dim vector', ms: 120, agent: 'Search Agent' },
  { icon: '🔍', label: 'pgvector HNSW', detail: 'cosine similarity, top 5', ms: 8, agent: 'Search Agent' },
  { icon: '📦', label: 'check_inventory', detail: '4 products verified', ms: 12, agent: 'Product Agent' },
];

export const MOCK_RESULTS = [
  { name: 'Nike Air Zoom Pegasus 41', price: 139.99, rating: 4.7, stock: 24, sim: 0.94 },
  { name: 'ASICS Gel-Nimbus 26', price: 159.99, rating: 4.8, stock: 12, sim: 0.91 },
  { name: 'Brooks Ghost 16', price: 139.99, rating: 4.6, stock: 31, sim: 0.87 },
];
