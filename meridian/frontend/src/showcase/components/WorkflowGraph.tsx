/**
 * WorkflowGraph — Phase 5 (LangGraph) StateGraph visualization.
 *
 * The topology is fixed and known (classify → branch → synthesize), so the
 * layout is hand-laid; but WHICH nodes and edges light up is derived entirely
 * from the real trace spans the OrchestrationAgent emits per turn:
 *   - node spans:        name "Workflow node: <name>" + field {node: <name>}
 *   - classified intent: field {intent: search|plan|availability|memory_recall}
 *   - checkpoints:       span name "Checkpoint · PostgresSaver.put" + the
 *                        ACTUAL checkpointer kind in field {checkpointer: ...}
 *
 * During "Replay trace" the activation is keyed on replayIndex so the path
 * lights up node-by-node in step with the span replay.
 *
 * Backend reference: backend/agents/orchestration_05/workflow.py
 */
import { motion } from 'framer-motion';
import type { MeridianShowcaseState } from '../hooks/useMeridianShowcase';
import type { ShowcaseTraceSpan } from '../lib/showcaseAdapters';

const prefersReducedMotion =
  typeof window !== 'undefined' &&
  typeof window.matchMedia === 'function' &&
  window.matchMedia('(prefers-reduced-motion: reduce)').matches;

type NodeName = 'classify' | 'search' | 'availability' | 'memory_recall' | 'synthesize';

// Hand-laid coordinates on a 0..300 x 0..150 canvas. classify on the left, the
// three branch workers stacked in the middle, synthesize on the right.
const NODE_LAYOUT: Record<NodeName, { x: number; y: number; label: string }> = {
  classify: { x: 26, y: 75, label: 'classify' },
  search: { x: 140, y: 26, label: 'search' },
  availability: { x: 140, y: 75, label: 'availability' },
  memory_recall: { x: 140, y: 124, label: 'memory' },
  synthesize: { x: 268, y: 75, label: 'synthesize' },
};

// The edges that light for each classified intent. Mirrors the conditional
// routing in workflow.py: plan = classify→search→availability→synthesize;
// search = classify→search→synthesize; etc.
const INTENT_EDGES: Record<string, [NodeName, NodeName][]> = {
  search: [['classify', 'search'], ['search', 'synthesize']],
  plan: [
    ['classify', 'search'],
    ['search', 'availability'],
    ['availability', 'synthesize'],
  ],
  availability: [['classify', 'availability'], ['availability', 'synthesize']],
  memory_recall: [['classify', 'memory_recall'], ['memory_recall', 'synthesize']],
};

const NODE_RE = /Workflow node:\s*(classify|search|availability|memory_recall|synthes)/i;

function spanNode(span: ShowcaseTraceSpan): NodeName | null {
  const field = span.fields?.find((f) => f.label.toLowerCase() === 'node')?.value;
  if (field && field in NODE_LAYOUT) return field as NodeName;
  const m = NODE_RE.exec(span.name || '');
  if (!m) return null;
  return (m[1].startsWith('synthes') ? 'synthesize' : m[1]) as NodeName;
}

interface GraphActivation {
  litNodes: Set<NodeName>;
  activeEdges: [NodeName, NodeName][];
  intent: string | null;
  checkpointer: string | null;
  checkpointAfter: Set<NodeName>;
}

function deriveActivation(
  spans: ShowcaseTraceSpan[],
  isReplaying: boolean,
  replayIndex: number,
): GraphActivation {
  const litNodes = new Set<NodeName>();
  const checkpointAfter = new Set<NodeName>();
  let intent: string | null = null;
  let checkpointer: string | null = null;
  let lastNode: NodeName | null = null;

  spans.forEach((span, i) => {
    // During replay, only consider spans up to the current replay cursor.
    if (isReplaying && replayIndex >= 0 && i > replayIndex) return;

    const node = spanNode(span);
    if (node) {
      litNodes.add(node);
      lastNode = node;
      const f = span.fields?.find((x) => x.label.toLowerCase() === 'intent')?.value;
      if (f) intent = f;
    }
    if (/checkpoint/i.test(span.name || '')) {
      const ck = span.fields?.find((x) => x.label.toLowerCase() === 'checkpointer')?.value;
      if (ck) checkpointer = ck;
      if (lastNode) checkpointAfter.add(lastNode);
    }
  });

  // Edges light only between nodes that are BOTH lit, following the intent map.
  const planned: [NodeName, NodeName][] = (intent && INTENT_EDGES[intent]) || [];
  const activeEdges = planned.filter(([a, b]) => litNodes.has(a) && litNodes.has(b));

  return { litNodes, activeEdges, intent, checkpointer, checkpointAfter };
}

// Build a smooth-ish path between two node centers.
function edgePath(a: NodeName, b: NodeName): string {
  const p = NODE_LAYOUT[a];
  const q = NODE_LAYOUT[b];
  const midX = (p.x + q.x) / 2;
  return `M ${p.x + 30} ${p.y} C ${midX} ${p.y}, ${midX} ${q.y}, ${q.x - 30} ${q.y}`;
}

export function WorkflowGraph({ state }: { state: MeridianShowcaseState }) {
  const { litNodes, activeEdges, intent, checkpointer, checkpointAfter } = deriveActivation(
    state.traceSpans,
    state.isReplaying,
    state.replayIndex,
  );

  if (litNodes.size === 0) return null;

  const allEdges: [NodeName, NodeName][] = [
    ['classify', 'search'],
    ['classify', 'availability'],
    ['classify', 'memory_recall'],
    ['search', 'availability'],
    ['search', 'synthesize'],
    ['availability', 'synthesize'],
    ['memory_recall', 'synthesize'],
  ];
  const isActiveEdge = (a: NodeName, b: NodeName) =>
    activeEdges.some(([x, y]) => x === a && y === b);

  return (
    <div className="mds-wfgraph" role="img" aria-label="LangGraph workflow path">
      <div className="mds-wfgraph-head">
        <span className="mds-wfgraph-title">LangGraph StateGraph</span>
        {intent && <span className="mds-wfgraph-intent">intent: {intent}</span>}
      </div>
      <svg viewBox="0 0 300 150" className="mds-wfgraph-svg" preserveAspectRatio="xMidYMid meet">
        {/* edges: idle ones faint, active ones draw + glow */}
        {allEdges.map(([a, b]) => {
          const active = isActiveEdge(a, b);
          return (
            <motion.path
              key={`${a}-${b}`}
              d={edgePath(a, b)}
              className={`mds-wfgraph-edge${active ? ' is-active' : ''}`}
              fill="none"
              initial={false}
              animate={
                prefersReducedMotion
                  ? { pathLength: active ? 1 : 0.001, opacity: active ? 1 : 0.18 }
                  : { pathLength: active ? 1 : 0.001, opacity: active ? 1 : 0.18 }
              }
              transition={prefersReducedMotion ? { duration: 0 } : { duration: 0.45, ease: 'easeInOut' }}
            />
          );
        })}
        {/* nodes */}
        {(Object.keys(NODE_LAYOUT) as NodeName[]).map((name) => {
          const { x, y, label } = NODE_LAYOUT[name];
          const lit = litNodes.has(name);
          return (
            <g key={name} className={`mds-wfgraph-node${lit ? ' is-lit' : ''}`}>
              <motion.rect
                x={x - 30}
                y={y - 13}
                width={60}
                height={26}
                rx={8}
                initial={false}
                animate={
                  prefersReducedMotion
                    ? { opacity: lit ? 1 : 0.35 }
                    : { opacity: lit ? 1 : 0.35, scale: lit ? 1 : 0.96 }
                }
                transition={prefersReducedMotion ? { duration: 0 } : { type: 'spring', stiffness: 360, damping: 26 }}
                style={{ transformBox: 'fill-box', transformOrigin: 'center' }}
              />
              <text x={x} y={y + 1} className="mds-wfgraph-node-label">
                {label}
              </text>
              {checkpointAfter.has(name) && name !== 'synthesize' && (
                <circle
                  cx={x + 30}
                  cy={y - 13}
                  r={4}
                  className="mds-wfgraph-ckpt"
                >
                  <title>
                    Checkpoint saved after {label} · {checkpointer ?? 'checkpointer'}
                  </title>
                </circle>
              )}
            </g>
          );
        })}
      </svg>
      {checkpointer && (
        <div className="mds-wfgraph-foot">
          <span className="mds-wfgraph-ckpt-dot" aria-hidden="true" />
          checkpointed · {checkpointer}
        </div>
      )}
    </div>
  );
}
