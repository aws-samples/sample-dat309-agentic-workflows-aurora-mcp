/**
 * traceAdapter — typed adapter helpers between the backend `ChatResponse` /
 * `MemoryProfileResponse` / `ProductListResponse` shapes and the data the
 * Meridian Pro UI surfaces want.
 *
 * The Meridian backend exposes a fairly rich `ActivityEntry` shape; the UI
 * just consumes specific projections. These helpers are intentionally tiny
 * and pure so they can be unit-tested or reused by both Pro and Demo Stage.
 *
 * The heavier "synthesize Phase 4 preamble + enrich missing telemetry" logic
 * still lives in `utils/traceTelemetry.ts`; that's intentional — the
 * adapters here only deal with mechanical projections, not narration.
 */
import type {
  ActivityEntry,
  ChatResponse,
  LongTermMemoryFact,
  MemoryProfileResponse,
  Message,
  Product,
} from '../types';

/* ───────────────────────── Trace spans ───────────────────────── */

export interface TraceSpanView {
  id: string;
  title: string;
  agent?: string;
  agentFile?: string;
  category: string;
  status: string;
  latencyMs: number | null;
  sql?: string;
  details?: string;
  tokensIn?: number;
  tokensOut?: number;
}

/**
 * activityTraceToSpans — flatten an `ActivityEntry[]` (the shape returned
 * inline in `POST /api/chat`) into UI-friendly span rows.
 */
export function activityTraceToSpans(activities: ActivityEntry[] | undefined): TraceSpanView[] {
  if (!activities?.length) return [];
  return activities.map((a, idx) => ({
    // Use `||` not `??` here: a backend serializer that emits "" for a
    // missing id would otherwise collide React keys. Both null and "" should
    // synthesize a unique fallback.
    id: a.id || `span-${idx}`,
    title: a.title,
    agent: a.agent_name ?? a.agentName,
    agentFile: a.agent_file ?? a.agentFile,
    category: a.telemetry?.category ?? 'runtime',
    status: a.telemetry?.status ?? 'ok',
    latencyMs: a.execution_time_ms ?? a.executionTimeMs ?? null,
    sql: a.sql_query ?? a.sqlQuery,
    details: a.details,
    tokensIn: a.telemetry?.tokens?.input,
    tokensOut: a.telemetry?.tokens?.output,
  }));
}

/* ───────────────────────── Messages ───────────────────────── */

/**
 * chatResponseToMessages — append the assistant response to an existing
 * message history. We keep the returned products/order on the message so the
 * chat pane can render them inline.
 */
export function chatResponseToMessages(
  prior: Message[],
  userText: string,
  response: ChatResponse | null,
): Message[] {
  const userMsg: Message = { role: 'user', text: userText };
  if (!response) return [...prior, userMsg];
  const reply: Message = response.products?.length
    ? { role: 'bot', type: 'products', text: response.message, products: response.products }
    : response.order
      ? { role: 'bot', type: 'order', text: response.message, order: response.order }
      : { role: 'bot', type: 'text', text: response.message };
  if (response.follow_ups?.length) reply.follow_ups = response.follow_ups;
  return [...prior, userMsg, reply];
}

/* ───────────────────────── Memory ───────────────────────── */

/**
 * memoryResponseToFacts — normalize a `GET /api/memory/{traveler_id}` response.
 */
export function memoryResponseToFacts(
  response: MemoryProfileResponse | null | undefined,
): LongTermMemoryFact[] {
  return response?.facts ?? [];
}

/* ───────────────────────── Trip catalog ───────────────────────── */

export interface TripCard {
  id: string;
  name: string;
  brand: string;
  category: string;
  description: string;
  price: number;
  imageUrl?: string;
  similarity?: number;
  tags: string[];
}

const TAG_BY_CATEGORY: Record<string, string[]> = {
  'City Breaks': ['Walkable', 'Refundable'],
  'Beach & Resort': ['Coastal', 'Adults only'],
  'Adventure & Outdoors': ['Hiking', 'Refundable'],
  'Wellness & Luxury': ['Spa', 'Slow pace'],
  'Business travel': ['Lounge access', '1-stop'],
};

/**
 * packagesResponseToTripCards — convert the backend `Product[]` shape into
 * polished trip cards. Cards include derived tags by category so the UI
 * doesn't need to embed marketing copy.
 */
export function packagesResponseToTripCards(products: Product[] | undefined): TripCard[] {
  if (!products?.length) return [];
  return products.map((p) => ({
    id: p.product_id,
    name: p.name,
    brand: p.brand,
    category: p.category,
    description: p.description ?? '',
    price: p.price,
    imageUrl: p.image_url,
    similarity: p.similarity,
    tags: TAG_BY_CATEGORY[p.category] ?? ['Refundable'],
  }));
}
