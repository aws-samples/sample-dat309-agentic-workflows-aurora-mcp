/**
 * Builds rich trace preamble + enriches backend activity spans with telemetry
 */
import type { Message, ActivityEntry } from '../types';

const LONG_TERM_FACTS = [
  { key: 'party_size', value: '2 travelers', source: 'booking_history', confidence: 0.98 },
  { key: 'goal', value: 'Tokyo culture trip — Oct 12–19', source: 'profile', confidence: 0.95 },
  { key: 'preference', value: 'Window seat · aisle on long-haul', source: 'browse_session', confidence: 0.91 },
  { key: 'allergy', value: 'Shellfish — exclude seafood dining', source: 'support_ticket', confidence: 1.0 },
  { key: 'budget', value: 'Prefers $2k–3.5k per person', source: 'search_analytics', confidence: 0.87 },
];

function span(
  partial: Omit<ActivityEntry, 'id' | 'timestamp'> & { id?: string }
): ActivityEntry {
  return {
    id: partial.id ?? `span-${Math.random().toString(36).slice(2, 9)}`,
    timestamp: new Date().toISOString(),
    ...partial,
  };
}

function shortTermItems(msgs: Message[], query: string): string[] {
  const recent = msgs.slice(-6).map((m) => `${m.role}: ${m.text.slice(0, 80)}${m.text.length > 80 ? '…' : ''}`);
  return [
    `current_turn: "${query.slice(0, 100)}"`,
    `turn_count: ${msgs.length + 1}`,
    ...recent,
    'tool_buffer: [search_results_v2, cart_state]',
    'session_vars: { locale: en-US, channel: web_demo }',
  ];
}

function buildPhase4Preamble(
  query: string,
  traceId: string,
  msgs: Message[]
): ActivityEntry[] {
  const conversationId = 'conv_meridian_demo';
  return [
    span({
      activity_type: 'reasoning',
      title: 'AgentCore session bootstrap',
      agent_name: 'runtime',
      agent_file: 'agentcore/session.py',
      execution_time_ms: 18,
      telemetry: {
        category: 'runtime',
        component: 'Bedrock AgentCore',
        status: 'ok',
        fields: [
          { label: 'trace_id', value: traceId, mono: true },
          { label: 'conversation_id', value: conversationId, mono: true },
          { label: 'runtime', value: 'meridian-travel-v3' },
          { label: 'region', value: 'us-east-1' },
          { label: 'governance', value: 'scopes: search, availability · budget: $4,000' },
        ],
      },
    }),
    span({
      activity_type: 'reasoning',
      title: 'Load short-term memory (session)',
      agent_name: 'memory_agent',
      agent_file: 'agents/memory_agent.py',
      execution_time_ms: 12,
      telemetry: {
        category: 'memory_short',
        component: 'AgentCore state',
        status: 'ok',
        memory: {
          shortTerm: {
            label: 'Session context window',
            items: shortTermItems(msgs, query),
          },
        },
        fields: [
          { label: 'window', value: 'last 6 turns + tool buffer' },
          { label: 'store', value: 'in-memory session (AgentCore)' },
          { label: 'ttl', value: '30 min idle' },
        ],
      },
    }),
    span({
      activity_type: 'database',
      title: 'Recall long-term memory (Aurora)',
      agent_name: 'memory_agent',
      agent_file: 'agents/memory_agent.py',
      execution_time_ms: 34,
      sql_query:
        "SELECT fact_key, fact_value, source, confidence FROM memory.facts WHERE user_id = $1 ORDER BY embedding <=> embed($2) LIMIT 8",
      telemetry: {
        category: 'memory_long',
        component: 'Aurora PostgreSQL',
        status: 'ok',
        memory: {
          longTerm: {
            label: 'Durable facts (pgvector recall)',
            facts: LONG_TERM_FACTS,
          },
        },
        fields: [
          { label: 'table', value: 'memory.facts' },
          { label: 'recall', value: 'vector similarity + recency' },
          { label: 'facts_matched', value: String(LONG_TERM_FACTS.length) },
          { label: 'applied_filters', value: 'party size, allergy, dates, budget' },
        ],
      },
    }),
    span({
      activity_type: 'reasoning',
      title: 'Supervisor routing (LangGraph)',
      agent_name: 'SupervisorAgent',
      agent_file: 'agents/phase3/supervisor.py',
      execution_time_ms: 28,
      telemetry: {
        category: 'orchestration',
        component: 'LangGraph',
        status: 'delegated',
        tokens: { input: 1240, output: 86 },
        fields: [
          { label: 'graph', value: 'meridian_supervisor_v2' },
          { label: 'intent', value: inferIntent(query) },
          { label: 'route', value: 'SearchAgent → hybrid_retrieval' },
          { label: 'memory_injected', value: 'yes — party of 2, Tokyo Oct, shellfish' },
        ],
      },
    }),
  ];
}

function buildPhase2Preamble(query: string, traceId: string, msgs: Message[]): ActivityEntry[] {
  return [
    span({
      activity_type: 'reasoning',
      title: 'Session context loaded',
      agent_name: 'Phase2Agent',
      agent_file: 'agents/phase2/agent.py',
      execution_time_ms: 8,
      telemetry: {
        category: 'memory_short',
        component: 'Strands runtime',
        status: 'ok',
        memory: {
          shortTerm: {
            label: 'Turn context',
            items: shortTermItems(msgs, query).slice(0, 4),
          },
        },
        fields: [
          { label: 'trace_id', value: traceId, mono: true },
          { label: 'long_term', value: 'not enabled in Phase 2' },
        ],
      },
    }),
    span({
      activity_type: 'mcp',
      title: 'MCP tool discovery',
      agent_name: 'MCPClient',
      agent_file: 'mcp/mcp_client.py',
      execution_time_ms: 22,
      telemetry: {
        category: 'tool',
        component: 'MCP Server',
        status: 'ok',
        fields: [
          { label: 'server', value: 'awslabs.postgres_mcp_server' },
          { label: 'tools', value: 'execute_sql, list_tables, describe_table' },
          { label: 'auth', value: 'IAM → RDS Data API' },
        ],
      },
    }),
  ];
}

function buildPhase1Preamble(_query: string, traceId: string): ActivityEntry[] {
  return [
    span({
      activity_type: 'reasoning',
      title: 'Direct agent invocation',
      agent_name: 'Phase1Agent',
      agent_file: 'agents/phase1/agent.py',
      execution_time_ms: 6,
      telemetry: {
        category: 'runtime',
        component: 'Strands + Bedrock',
        status: 'ok',
        fields: [
          { label: 'trace_id', value: traceId, mono: true },
          { label: 'memory', value: 'none — stateless turn' },
          { label: 'path', value: 'hardcoded tools → RDS Data API' },
        ],
      },
    }),
  ];
}

function inferIntent(query: string): string {
  const q = query.toLowerCase();
  if (q.includes('stock') || q.includes('available') || q.includes('dates')) return 'availability_check';
  if (q.includes('order') || q.includes('buy') || q.includes('book')) return 'booking_intent';
  if (q.includes('romantic') || q.includes('weekend') || q.includes('family')) return 'semantic_trip_search';
  return 'trip_discovery';
}

function enrichActivity(a: ActivityEntry, phase: 1 | 2 | 3 | 4, query: string): ActivityEntry {
  if (a.telemetry) return a;

  const base = { ...a };
  const type = a.activity_type;

  if (type === 'embedding') {
    base.telemetry = {
      category: 'model',
      component: 'Amazon Bedrock',
      status: 'ok',
      tokens: { input: Math.max(12, Math.floor(query.length / 4)) },
      fields: [
        { label: 'model', value: 'cohere.embed-v4:0' },
        { label: 'dimensions', value: '1024' },
        { label: 'input', value: `"${query.slice(0, 48)}${query.length > 48 ? '…' : ''}"` },
      ],
    };
  } else if (type === 'search') {
    base.telemetry = {
      category: 'data',
      component: 'Aurora PostgreSQL',
      status: phase >= 3 ? 'ok' : 'ok',
      fields:
        phase >= 3
          ? [
              { label: 'strategy', value: 'hybrid retrieval' },
              { label: 'semantic_weight', value: '0.70 (pgvector HNSW)' },
              { label: 'lexical_weight', value: '0.30 (tsvector/ts_rank)' },
              ...(phase === 4
                ? [{ label: 'memory_boost', value: 'party of 2 · Tokyo Oct · shellfish · budget filters' }]
                : []),
            ]
          : [
              { label: 'strategy', value: phase === 2 ? 'MCP → ILIKE' : 'ILIKE keyword' },
              { label: 'index', value: 'btree + sequential scan' },
            ],
    };
  } else if (type === 'mcp') {
    base.telemetry = {
      category: 'tool',
      component: 'MCP',
      status: a.title.toLowerCase().includes('discover') ? 'ok' : 'streaming',
      fields: [
        { label: 'protocol', value: 'Model Context Protocol v1' },
        { label: 'transport', value: 'stdio / SSE' },
        { label: 'operation', value: a.title },
      ],
    };
  } else if (type === 'database') {
    base.telemetry = {
      category: 'data',
      component: 'RDS Data API',
      status: 'ok',
      fields: [
        { label: 'api', value: 'ExecuteStatement' },
        { label: 'cluster', value: 'meridian-demo' },
        { label: 'database', value: 'meridian' },
      ],
    };
  } else if (type === 'delegation' || (type === 'reasoning' && a.agent_name?.includes('Supervisor'))) {
    base.telemetry = {
      category: 'orchestration',
      component: 'LangGraph',
      status: 'delegated',
      fields: [
        { label: 'from', value: a.agent_name ?? 'Supervisor' },
        { label: 'action', value: a.title },
        { label: 'details', value: a.details ?? '—' },
      ],
    };
  } else if (type === 'inventory') {
    base.telemetry = {
      category: 'tool',
      component: 'InventoryAgent',
      status: 'ok',
      fields: [
        { label: 'check', value: 'real-time stock via Aurora' },
        { label: 'sizes', value: 'available_sizes JSON' },
      ],
    };
  } else if (type === 'result') {
    base.telemetry = {
      category: 'synthesis',
      component: 'Claude on Bedrock',
      status: 'ok',
      tokens: { input: 890, output: 210 },
      fields: [
        { label: 'model', value: 'global.anthropic.claude-opus-4-7-v1' },
        { label: 'format', value: 'trip_cards + natural language' },
        { label: 'grounding', value: 'Aurora rows + memory facts' },
      ],
    };
  } else if (type === 'order') {
    base.telemetry = {
      category: 'synthesis',
      component: 'BookingAgent',
      status: 'held',
      fields: [
        { label: 'flow', value: 'plan → confirm → book' },
        { label: 'policy', value: 'charge scope ≤ $4,000' },
      ],
    };
  }

  return base;
}

function buildSynthesisStep(phase: 1 | 2 | 3 | 4, productCount: number): ActivityEntry {
  return span({
    activity_type: 'result',
    title: 'Compose grounded response',
    agent_name: phase >= 3 ? (phase === 4 ? 'PartnerRuntime' : 'SupervisorAgent') : `Phase${phase}Agent`,
    agent_file:
      phase === 4
        ? 'agents/phase4/partner_runtime.py'
        : phase === 3
          ? 'agents/phase3/supervisor.py'
          : `agents/phase${phase}/agent.py`,
    execution_time_ms: 45 + phase * 10,
    telemetry: {
      category: 'synthesis',
      component: 'Claude on Bedrock',
      status: phase === 4 ? 'ok' : 'ok',
      tokens: { input: 1100 + productCount * 120, output: 180 + productCount * 40 },
      fields: [
        {
          label: 'grounding_sources',
          value: `Aurora (${productCount} packages)${phase === 4 ? ' + memory.facts + session' : ''}`,
        },
        { label: 'hallucination_guard', value: 'row-level citations required' },
        { label: 'output', value: 'message + trip_cards' },
      ],
    },
  });
}

export function enrichTraceActivities(
  phase: 1 | 2 | 3 | 4,
  query: string,
  activities: ActivityEntry[],
  traceId: string,
  msgs: Message[],
  options?: { productCount?: number }
): ActivityEntry[] {
  const hasBackendMemory = activities.some(
    (a) => a.telemetry?.memory || a.activity_type === 'tool_call'
  );

  const preamble =
    phase === 4 && hasBackendMemory
      ? []
      : phase === 4
        ? buildPhase4Preamble(query, traceId, msgs)
        : phase === 2
          ? buildPhase2Preamble(query, traceId, msgs)
          : phase === 1
            ? buildPhase1Preamble(query, traceId)
            : [];

  const enriched = activities.map((a) => {
    if (a.telemetry) return a;
    return enrichActivity(a, phase, query);
  });

  const hasResult = enriched.some((a) => a.activity_type === 'result');
  const tail =
    !hasResult && options?.productCount !== undefined && options.productCount > 0
      ? [buildSynthesisStep(phase, options.productCount)]
      : [];

  return [...preamble, ...enriched, ...tail];
}
