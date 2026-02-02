/**
 * Mock Data Provider
 * 
 * 30 products across 6 categories for offline demo mode.
 * Requirements: 7.1, 7.2
 */

import { Product, ActivityEntry, ChatResponse } from '../types'

// Mock Products - 30 products across 6 categories
export const mockProducts: Product[] = [
  // Running Shoes (5)
  { product_id: 'RS001', name: 'CloudRunner Pro', brand: 'Nike', price: 159.99, description: 'Lightweight running shoe with responsive cushioning for daily training', image_url: '/images/cloudrunner-pro.jpg', category: 'Running Shoes', available_sizes: ['7', '8', '9', '10', '11', '12'] },
  { product_id: 'RS002', name: 'UltraBoost 24', brand: 'Adidas', price: 189.99, description: 'Premium running shoe with energy-returning Boost midsole', image_url: '/images/ultraboost-24.jpg', category: 'Running Shoes', available_sizes: ['7', '8', '9', '10', '11'] },
  { product_id: 'RS003', name: 'Ghost 16', brand: 'Brooks', price: 139.99, description: 'Smooth transitions and soft cushioning for neutral runners', image_url: '/images/ghost-16.jpg', category: 'Running Shoes', available_sizes: ['8', '9', '10', '11', '12'] },
  { product_id: 'RS004', name: 'Pegasus 41', brand: 'Nike', price: 129.99, description: 'Versatile everyday trainer with React foam cushioning', image_url: '/images/pegasus-41.jpg', category: 'Running Shoes', available_sizes: ['7', '8', '9', '10', '11', '12'] },
  { product_id: 'RS005', name: 'Fresh Foam X', brand: 'New Balance', price: 149.99, description: 'Plush cushioning for long-distance comfort', image_url: '/images/fresh-foam-x.jpg', category: 'Running Shoes', available_sizes: ['8', '9', '10', '11'] },

  // Training Shoes (5)
  { product_id: 'TS001', name: 'Metcon 9', brand: 'Nike', price: 149.99, description: 'Stable platform for weightlifting and HIIT workouts', image_url: '/images/metcon-9.jpg', category: 'Training Shoes', available_sizes: ['7', '8', '9', '10', '11', '12'] },
  { product_id: 'TS002', name: 'Nano X4', brand: 'Reebok', price: 139.99, description: 'Versatile cross-training shoe for gym and functional fitness', image_url: '/images/nano-x4.jpg', category: 'Training Shoes', available_sizes: ['8', '9', '10', '11'] },
  { product_id: 'TS003', name: 'Dropset 2', brand: 'Adidas', price: 129.99, description: 'Low-profile trainer for strength and agility work', image_url: '/images/dropset-2.jpg', category: 'Training Shoes', available_sizes: ['7', '8', '9', '10', '11', '12'] },
  { product_id: 'TS004', name: 'NOBULL Trainer+', brand: 'NOBULL', price: 159.99, description: 'Durable trainer built for intense CrossFit workouts', image_url: '/images/nobull-trainer.jpg', category: 'Training Shoes', available_sizes: ['8', '9', '10', '11'] },
  { product_id: 'TS005', name: 'SuperRep Go 3', brand: 'Nike', price: 119.99, description: 'Lightweight shoe for cardio and circuit training', image_url: '/images/superrep-go.jpg', category: 'Training Shoes', available_sizes: ['7', '8', '9', '10', '11'] },

  // Fitness Equipment (5)
  { product_id: 'FE001', name: 'Adjustable Dumbbell Set', brand: 'Bowflex', price: 349.99, description: 'Space-saving dumbbells adjustable from 5-52.5 lbs', image_url: '/images/bowflex-dumbbells.jpg', category: 'Fitness Equipment' },
  { product_id: 'FE002', name: 'Resistance Band Kit', brand: 'TheraBand', price: 49.99, description: 'Set of 5 resistance levels for strength training', image_url: '/images/resistance-bands.jpg', category: 'Fitness Equipment' },
  { product_id: 'FE003', name: 'Yoga Mat Pro', brand: 'Manduka', price: 89.99, description: 'Premium 6mm thick mat with superior grip', image_url: '/images/yoga-mat-pro.jpg', category: 'Fitness Equipment' },
  { product_id: 'FE004', name: 'Kettlebell Set', brand: 'Rogue', price: 199.99, description: 'Cast iron kettlebells: 15, 25, and 35 lb set', image_url: '/images/kettlebell-set.jpg', category: 'Fitness Equipment' },
  { product_id: 'FE005', name: 'Pull-Up Bar', brand: 'Iron Gym', price: 39.99, description: 'Doorway pull-up bar with multiple grip positions', image_url: '/images/pullup-bar.jpg', category: 'Fitness Equipment' },

  // Apparel (5)
  { product_id: 'AP001', name: 'Dri-FIT Running Tee', brand: 'Nike', price: 45.00, description: 'Moisture-wicking performance shirt for running', image_url: '/images/drifit-tee.jpg', category: 'Apparel', available_sizes: ['S', 'M', 'L', 'XL'] },
  { product_id: 'AP002', name: 'Compression Shorts', brand: 'Under Armour', price: 35.00, description: 'Supportive compression fit for high-intensity training', image_url: '/images/compression-shorts.jpg', category: 'Apparel', available_sizes: ['S', 'M', 'L', 'XL'] },
  { product_id: 'AP003', name: 'Training Hoodie', brand: 'Adidas', price: 75.00, description: 'Lightweight hoodie for warm-ups and cool-downs', image_url: '/images/training-hoodie.jpg', category: 'Apparel', available_sizes: ['S', 'M', 'L', 'XL', 'XXL'] },
  { product_id: 'AP004', name: 'Running Leggings', brand: 'Lululemon', price: 98.00, description: 'High-waisted leggings with phone pocket', image_url: '/images/running-leggings.jpg', category: 'Apparel', available_sizes: ['XS', 'S', 'M', 'L'] },
  { product_id: 'AP005', name: 'Gym Tank Top', brand: 'Gymshark', price: 32.00, description: 'Breathable tank for weightlifting and cardio', image_url: '/images/gym-tank.jpg', category: 'Apparel', available_sizes: ['S', 'M', 'L', 'XL'] },

  // Accessories (5)
  { product_id: 'AC001', name: 'Fitness Tracker', brand: 'Fitbit', price: 149.99, description: 'Track steps, heart rate, and sleep quality', image_url: '/images/fitness-tracker.jpg', category: 'Accessories' },
  { product_id: 'AC002', name: 'Wireless Earbuds', brand: 'Beats', price: 199.99, description: 'Sweat-resistant earbuds with secure fit', image_url: '/images/wireless-earbuds.jpg', category: 'Accessories' },
  { product_id: 'AC003', name: 'Gym Bag', brand: 'Nike', price: 65.00, description: 'Spacious duffel with shoe compartment', image_url: '/images/gym-bag.jpg', category: 'Accessories' },
  { product_id: 'AC004', name: 'Water Bottle', brand: 'Hydro Flask', price: 44.95, description: '32oz insulated bottle keeps drinks cold 24hrs', image_url: '/images/water-bottle.jpg', category: 'Accessories' },
  { product_id: 'AC005', name: 'Lifting Gloves', brand: 'Harbinger', price: 29.99, description: 'Padded gloves for grip and wrist support', image_url: '/images/lifting-gloves.jpg', category: 'Accessories' },

  // Recovery (5)
  { product_id: 'RC001', name: 'Foam Roller', brand: 'TriggerPoint', price: 39.99, description: 'High-density roller for muscle recovery', image_url: '/images/foam-roller.jpg', category: 'Recovery' },
  { product_id: 'RC002', name: 'Massage Gun', brand: 'Theragun', price: 299.99, description: 'Percussive therapy device for deep tissue relief', image_url: '/images/massage-gun.jpg', category: 'Recovery' },
  { product_id: 'RC003', name: 'Compression Socks', brand: 'CEP', price: 59.99, description: 'Graduated compression for recovery and travel', image_url: '/images/compression-socks.jpg', category: 'Recovery', available_sizes: ['S', 'M', 'L', 'XL'] },
  { product_id: 'RC004', name: 'Ice Pack Set', brand: 'Chattanooga', price: 24.99, description: 'Reusable gel packs for injury treatment', image_url: '/images/ice-pack-set.jpg', category: 'Recovery' },
  { product_id: 'RC005', name: 'Muscle Balm', brand: 'Tiger Balm', price: 12.99, description: 'Topical analgesic for sore muscles', image_url: '/images/muscle-balm.jpg', category: 'Recovery' },
]

// Phase-specific response delays (ms) - Requirement 7.3
export const phaseDelays = {
  1: { min: 1500, max: 2500 },
  2: { min: 2000, max: 3500 },
  3: { min: 2500, max: 4500 },
}

// Generate random delay within phase range
export function getPhaseDelay(phase: 1 | 2 | 3): number {
  const { min, max } = phaseDelays[phase]
  return Math.floor(Math.random() * (max - min + 1)) + min
}

// Search products by query
export function searchProducts(query: string, limit = 5): Product[] {
  const lowerQuery = query.toLowerCase()
  const results = mockProducts.filter(p =>
    p.name.toLowerCase().includes(lowerQuery) ||
    p.description.toLowerCase().includes(lowerQuery) ||
    p.category.toLowerCase().includes(lowerQuery) ||
    p.brand.toLowerCase().includes(lowerQuery)
  )
  
  // Add mock similarity scores
  return results.slice(0, limit).map(p => ({
    ...p,
    similarity: 0.7 + Math.random() * 0.3, // 0.7-1.0
  }))
}

// Generate mock activity entries
export function generateMockActivities(phase: 1 | 2 | 3, query: string): ActivityEntry[] {
  const activities: ActivityEntry[] = []
  const now = new Date()

  if (phase === 1) {
    activities.push({
      id: crypto.randomUUID(),
      timestamp: new Date(now.getTime() - 1500).toISOString(),
      activity_type: 'embedding',
      title: 'Generated query embedding',
      details: 'Created 1024-dimensional vector using Nova Multimodal Embeddings',
      execution_time_ms: 245,
    })
    activities.push({
      id: crypto.randomUUID(),
      timestamp: new Date(now.getTime() - 1000).toISOString(),
      activity_type: 'search',
      title: 'Semantic product search',
      sql_query: `SELECT * FROM semantic_product_search('${query}', 5)`,
      execution_time_ms: 89,
    })
  } else if (phase === 2) {
    activities.push({
      id: crypto.randomUUID(),
      timestamp: new Date(now.getTime() - 2000).toISOString(),
      activity_type: 'mcp',
      title: 'MCP tool discovery',
      details: 'Connected to postgres-mcp-server, discovered 12 tools',
      execution_time_ms: 156,
    })
    activities.push({
      id: crypto.randomUUID(),
      timestamp: new Date(now.getTime() - 1200).toISOString(),
      activity_type: 'mcp',
      title: 'Executed query via MCP',
      details: 'Used execute_sql tool through RDS Data API',
      execution_time_ms: 312,
    })
  } else {
    activities.push({
      id: crypto.randomUUID(),
      timestamp: new Date(now.getTime() - 3000).toISOString(),
      activity_type: 'delegation',
      title: 'Supervisor delegated to Search Agent',
      agent_name: 'Supervisor',
      execution_time_ms: 45,
    })
    activities.push({
      id: crypto.randomUUID(),
      timestamp: new Date(now.getTime() - 2000).toISOString(),
      activity_type: 'embedding',
      title: 'Generated multimodal embedding',
      agent_name: 'Search Agent',
      details: 'Nova Multimodal Embeddings 1024-dim vector',
      execution_time_ms: 289,
    })
    activities.push({
      id: crypto.randomUUID(),
      timestamp: new Date(now.getTime() - 1000).toISOString(),
      activity_type: 'search',
      title: 'Vector similarity search',
      agent_name: 'Search Agent',
      sql_query: `SELECT * FROM semantic_product_search($1, 5)`,
      execution_time_ms: 67,
    })
  }

  return activities
}

// Generate mock chat response
export function generateMockResponse(
  message: string,
  phase: 1 | 2 | 3
): ChatResponse {
  const lowerMessage = message.toLowerCase()
  
  // Check for product search intent
  if (lowerMessage.includes('show') || lowerMessage.includes('find') || 
      lowerMessage.includes('search') || lowerMessage.includes('looking for')) {
    const products = searchProducts(message)
    return {
      message: `I found ${products.length} products that match your search. Here are the top results:`,
      products,
      activities: generateMockActivities(phase, message),
    }
  }

  // Check for order intent
  if (lowerMessage.includes('order') || lowerMessage.includes('buy') || 
      lowerMessage.includes('purchase')) {
    return {
      message: 'I\'ve processed your order. Here are the details:',
      order: {
        order_id: `ORD-${Date.now().toString(36).toUpperCase()}`,
        items: [
          { product_id: 'RS001', name: 'CloudRunner Pro', size: '10', quantity: 1, unit_price: 159.99 },
        ],
        subtotal: 159.99,
        tax: 13.60,
        shipping: 0,
        total: 173.59,
        status: 'confirmed',
        estimated_delivery: 'March 5-7, 2026',
      },
      activities: generateMockActivities(phase, message),
    }
  }

  // Default response
  return {
    message: `[Phase ${phase}] I can help you find products, check inventory, or place orders. Try asking me to "show running shoes" or "find fitness equipment".`,
    activities: generateMockActivities(phase, message),
  }
}
