/**
 * HowItWorksSection — Meridian Pro Journey rail
 *
 * Five-stop journey (SQL → MCP → Retrieval → Memory → Orchestration)
 * with done / live / next states.
 */
import { FadeIn } from '../components/FadeIn';
import { useAgentBridge } from '../context/AgentBridge';
import type { Phase } from '../types';

type StepState = 'done' | 'live' | 'next';

interface JourneyStep {
  num: string;
  state: StepState;
  ph: string;
  title: string;
  serif: string;
  desc: string;
  chips: string[];
  scale: string;
  persona: string;
  skills: string[];
}

const steps: JourneyStep[] = [
  {
    num: '01',
    state: 'live',
    ph: 'Phase 01',
    title: 'SQL',
    serif: '',
    desc: 'Plain SQL filters on trip_packages via the RDS Data API. The fastest possible answer for an exact match.',
    chips: ['RDS Data API', 'SQL · WHERE'],
    scale: '~50 trips/day · two founders, one ops console',
    persona: 'Alex types “Beach & Resort under $1500” — a SQL WHERE clause returns 3 packages.',
    skills: ['sql_filter'],
  },
  {
    num: '02',
    state: 'live',
    ph: 'Phase 02',
    title: 'MCP',
    serif: '',
    desc: 'Same queries reframed as MCP tool calls — postgres-mcp-server exposes run_query with a typed schema and dry-run.',
    chips: ['postgres-mcp-server', 'tool registry'],
    scale: '~500 trips/day · booking, pricing, and support agents share one catalog',
    persona: 'Three agents, one Aurora. None of them re-implement the SQL.',
    skills: ['run_query'],
  },
  {
    num: '03',
    state: 'live',
    ph: 'Phase 03',
    title: 'Retrieval',
    serif: '',
    desc: 'Hybrid pgvector + tsvector. Vague requests resolve to the right packages. A Strands supervisor delegates to specialists.',
    chips: ['pgvector HNSW', 'tsvector', 'Cohere v4'],
    scale: '~5,000 trips/day · customer-facing natural language',
    persona: 'Alex: “romantic week in Europe.” Keywords would miss; embeddings find Tuscany.',
    skills: ['search', 'availability', 'booking'],
  },
  {
    num: '04',
    state: 'live',
    ph: 'Phase 04',
    title: 'Memory',
    serif: '',
    desc: 'A ConciergeOrchestrator grounds every turn in traveler_profiles and a Strands @tool memory agent. Memory in, recommendations out.',
    chips: ['Strands @tool', 'trip_interactions', 'Aurora memory'],
    scale: '~50,000 trips/day · returning travelers expect to be known',
    persona: 'Alex returns: “Tokyo for two in October.” Party size, allergy, budget — already known.',
    skills: ['recall_session', 'recall_facts', 'similar_trips', 'persist_turn'],
  },
  {
    num: '05',
    state: 'live',
    ph: 'Phase 05',
    title: 'Orchestration',
    serif: '',
    desc: 'A LangGraph StateGraph owns control flow — classify, branch, synthesize — with checkpointed state in Aurora.',
    chips: ['LangGraph', 'StateGraph', 'PostgresSaver'],
    scale: '~500,000 trips/day · multi-step workflows that span weeks',
    persona: 'Alex: “Watch our Tokyo dates and rebook the hotel if we slip a week.” Checkpointed in Aurora.',
    skills: ['classify', 'checkpoint', 'synthesize'],
  },
];

const STEP_PHASE: Record<string, Phase> = {
  '01': 1,
  '02': 2,
  '03': 3,
  '04': 4,
  '05': 5,
};

export function HowItWorksSection() {
  const { openConcierge } = useAgentBridge();

  return (
    <section id="howitworks" className="mp-section">
      <FadeIn>
        <div className="mp-section-h-row">
          <div className="mp-section-h">
            <div className="mp-label-row">Phases 1–5 · the ladder</div>
            <h2>From SQL to orchestration.</h2>
            <p>
              Each phase climbs a rung: plain SQL, then MCP, then hybrid retrieval, then traveler
              memory, finally an explicit LangGraph StateGraph that owns control flow. The console
              below lets you scrub through all five on the same query.
            </p>
          </div>
          <div className="actions">
            <button
              type="button"
              className="mp-btn ghost sm"
              onClick={() => openConcierge({ phase: 1, clear: true, focus: true })}
            >
              Compare modes
            </button>
            <button
              type="button"
              className="mp-btn primary sm"
              onClick={() => openConcierge({ phase: 4, focus: true })}
            >
              Open console ↗
            </button>
          </div>
        </div>
      </FadeIn>

      <FadeIn delay={0.1}>
        <div className="mp-journey">
          <div className="mp-journey-rail">
            {steps.map((s) => (
              <button
                key={s.num}
                type="button"
                className={`mp-journey-step ${s.state}`}
                onClick={() =>
                  openConcierge({ phase: STEP_PHASE[s.num], focus: true })
                }
              >
                <span className="ph">{s.ph}</span>
                <div className="node">{s.num.slice(-1)}</div>
                <div className="ttl">{s.title}</div>
                <div className="desc">{s.desc}</div>
                <div className="mp-journey-arc">
                  <div className="arc-row">
                    <span className="arc-label">At this scale</span>
                    <span className="arc-text">{s.scale}</span>
                  </div>
                  <div className="arc-row">
                    <span className="arc-label">Alex &amp; Jordan</span>
                    <span className="arc-text">{s.persona}</span>
                  </div>
                  <div className="arc-row">
                    <span className="arc-label">Skills</span>
                    <span className="arc-skills">
                      {s.skills.map((sk) => (
                        <code key={sk} className="arc-skill">{sk}</code>
                      ))}
                    </span>
                  </div>
                </div>
                <div className="stack">
                  {s.chips.map((c) => (
                    <span key={c} className="chip">
                      {c}
                    </span>
                  ))}
                </div>
              </button>
            ))}
          </div>
        </div>
      </FadeIn>
    </section>
  );
}
