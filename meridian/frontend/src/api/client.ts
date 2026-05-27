/**
 * API client for Meridian backend
 */
import type {
  ChatRequest,
  ChatResponse,
  MemoryProfileResponse,
  OrderRequest,
  OrderResponse,
  PackageListResponse,
  Product,
  ProductListResponse,
  TripPackage,
} from '../types';

const API_BASE = 'http://localhost:8000/api';

function packageToProduct(pkg: TripPackage): Product {
  return {
    product_id: pkg.package_id,
    name: pkg.name,
    brand: pkg.operator,
    price: pkg.price_per_person,
    description: pkg.description,
    image_url: pkg.image_url,
    category: pkg.trip_type,
    available_sizes: pkg.durations,
    similarity: pkg.similarity,
  };
}

function productToPackage(product: Product): TripPackage {
  return {
    package_id: product.product_id,
    name: product.name,
    trip_type: product.category,
    destination: '',
    region: '',
    price_per_person: product.price,
    operator: product.brand,
    description: product.description,
    image_url: product.image_url,
    durations: product.available_sizes,
    availability: null,
    highlights: null,
    similarity: product.similarity,
  };
}

/**
 * Fetch native trip packages from the backend.
 *
 * `/api/packages` is the travel-native contract. If an older backend only
 * exposes the legacy `/api/products` shape, this adapter preserves the same
 * typed frontend API while keeping the UI on trip language.
 */
export async function fetchPackages(category?: string, limit = 50, featured = false): Promise<TripPackage[]> {
  const params = new URLSearchParams();
  if (category) params.set('category', category);
  params.set('limit', limit.toString());
  if (featured) params.set('featured', 'true');

  try {
    const response = await fetch(`${API_BASE}/packages?${params}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch packages: ${response.statusText}`);
    }
    const data: PackageListResponse = await response.json();
    return data.packages;
  } catch (primaryError) {
    const response = await fetch(`${API_BASE}/products?${params}`);
    if (!response.ok) {
      throw primaryError instanceof Error
        ? primaryError
        : new Error(`Failed to fetch packages: ${response.statusText}`);
    }
    const data: ProductListResponse = await response.json();
    return data.products.map(productToPackage);
  }
}

/**
 * Fetch all products from the backend
 */
export async function fetchProducts(category?: string, limit = 50, featured = false): Promise<Product[]> {
  const packages = await fetchPackages(category, limit, featured);
  return packages.map(packageToProduct);
}

/**
 * Fetch a single product by ID
 */
export async function fetchProduct(productId: string): Promise<Product> {
  try {
    const response = await fetch(`${API_BASE}/packages/${productId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch package: ${response.statusText}`);
    }
    const data: TripPackage = await response.json();
    return packageToProduct(data);
  } catch (primaryError) {
    const response = await fetch(`${API_BASE}/products/${productId}`);
    if (!response.ok) {
      throw primaryError instanceof Error
        ? primaryError
        : new Error(`Failed to fetch product: ${response.statusText}`);
    }
    return response.json();
  }
}

/**
 * Send a chat message to the AI assistant
 */
export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });
  
  if (!response.ok) {
    throw new Error(`Chat request failed: ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Fetch long-term memory profile from Aurora (Phase 4)
 */
export async function fetchMemoryProfile(travelerId = 'trv_meridian_demo'): Promise<MemoryProfileResponse> {
  const response = await fetch(`${API_BASE}/memory/${travelerId}`);
  if (!response.ok) {
    throw new Error(`Memory profile request failed: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Perform semantic search for products
 */
export async function searchProducts(query: string, phase: 1 | 2 | 3 = 3): Promise<ChatResponse> {
  return sendChatMessage({
    message: query,
    phase,
  });
}

/**
 * Process an order for a product
 */
export async function processOrder(request: OrderRequest): Promise<OrderResponse> {
  const response = await fetch(`${API_BASE}/chat/order`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Order request failed: ${response.statusText}`);
  }

  return response.json();
}
