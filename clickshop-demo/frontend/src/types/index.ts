/**
 * TypeScript types for ClickShop frontend
 */

export interface Product {
  product_id: string;
  name: string;
  brand: string;
  price: number;
  description: string;
  image_url: string;
  category: string;
  available_sizes?: string[] | null;
  similarity?: number;
}

export interface ProductListResponse {
  products: Product[];
  total: number;
}

export type ActivityType = 'search' | 'embedding' | 'tool_call' | 'database' | 'error' | 'inventory' | 'order' | 'delegation' | 'mcp';

export interface ActivityEntry {
  id: string;
  timestamp: string;
  activity_type: ActivityType;
  title: string;
  details?: string;
  sql_query?: string;
  execution_time_ms?: number;
  agent_name?: string;
  // Aliases for camelCase access
  type?: ActivityType;
  agentName?: string;
  executionTimeMs?: number;
  sqlQuery?: string;
}

export interface OrderItem {
  product_id: string;
  name: string;
  size?: string;
  quantity: number;
  unit_price: number;
}

export interface Order {
  order_id: string;
  items: OrderItem[];
  subtotal: number;
  tax: number;
  shipping: number;
  total: number;
  status: string;
  estimated_delivery?: string;
}

export interface ChatRequest {
  message: string;
  phase: 1 | 2 | 3;
  customer_id?: string;
  conversation_id?: string;
}

export interface ChatResponse {
  message: string;
  products?: Product[];
  order?: Order;
  activities: ActivityEntry[];
}

export interface Message {
  role: 'user' | 'bot';
  type?: 'text' | 'products' | 'order';
  text: string;
  products?: Product[];
  order?: Order;
}

// Alias for backward compatibility
export type ChatMessage = Message;

export interface PhaseInfo {
  id: 1 | 2 | 3;
  name: string;
  description: string;
  color: string;
}
