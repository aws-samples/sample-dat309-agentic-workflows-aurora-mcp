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
    ph: 'Phase 01 · Retrieval stack',
    title: 'SQL',
    serif: '',
    desc: 'The lab. Direct RDS Data API. Fast for exact matches — and it breaks on "romantic week in Europe."',
    chips: ['RDS Data API', 'SQL · WHERE'],
    scale: '~50 trips/day · two founders, one ops console',
    persona: 'Alex types "Beach & Resort under $1500" — a SQL WHERE clause returns 3 packages.',
    skills: ['sql_filter'],
  },
  {
    num: '02',
    state: 'live',
    ph: 'Phase 02 · Retrieval stack',
    title: 'MCP',
    serif: '',
    desc: 'MCP changes the interface, not the intelligence. Typed tool, IAM auth — same gap on natural language.',
    chips: ['postgres-mcp-server', 'tool registry'],
    scale: '~500 trips/day · booking, pricing, and support agents share one catalog',
    persona: 'Three agents, one Aurora. None of them re-implement the SQL — but "romantic" still misses.',
    skills: ['run_query'],
  },
  {
    num: '03',
    state: 'live',
    ph: 'Phase 03 · Retrieval stack',
    title: 'Retrieval',
    serif: '',
    desc: 'Where natural language works. Cohere Embed v4 + hybrid pgvector + tsvector. Strands supervisor delegates to specialists.',
    chips: ['pgvector HNSW', 'tsvector', 'Cohere v4', 'Strands supervisor'],
    scale: '~5,000 trips/day · customer-facing natural language',
    persona: 'Alex: "romantic week in Europe." Keywords would miss; embeddings find Tuscany.',
    skills: ['search', 'availability', 'booking'],
  },
  {
    num: '04',
    state: 'live',
    ph: 'Phase 04 · Production',
    title: 'Memory',
    serif: '',
    desc: 'The concierge knows Alex & Jordan, their Tokyo trip Oct 12–19, the shellfish allergy. None of that\'s in the prompt — it\'s in Aurora. RLS pins per-traveler scope inside an RDS Data API transaction; every turn writes one audit row; AgentCore Memory mirrors session events.',
    chips: ['traveler_preferences', 'RLS · Data API tx', 'audit log', 'AgentCore Memory'],
    scale: '~50,000 trips/day · returning travelers expect to be known',
    persona: 'Alex returns: "Tokyo for two in October." Party size, allergy, budget — already known.',
    skills: ['recall_session', 'recall_facts', 'similar_trips', 'persist_turn'],
  },
  {
    num: '05',
    state: 'live',
    ph: 'Phase 05 · Orchestration',
    title: 'Orchestration',
    serif: '',
    desc: 'LangGraph owns control flow when we want it inspectable, branchable, resumable. Explicit StateGraph + conditional edges + PostgresSaver checkpoints in Aurora. Strands routes tools when the agent picks the call. Together: AgentCore + LangGraph + Strands.',
    chips: ['LangGraph', 'StateGraph', 'PostgresSaver', 'AgentCore'],
    scale: '~500,000 trips/day · multi-step workflows that span weeks',
    persona: 'Alex: "Watch our Tokyo dates and rebook the hotel if we slip a week." Checkpointed in Aurora.',
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
            <div className="mp-label-row">Three acts · five phases</div>
            <h2>The retrieval stack, then production, then orchestration.</h2>
            <p>
              Phases 1–3 are the <em>retrieval stack</em>: SQL is the lab, MCP changes the interface,
              retrieval is where natural language actually works. Phase 4 is the <em>production
              story</em> — the concierge knows the traveler because Aurora does. Phase 5 is{' '}
              <em>orchestration</em> — LangGraph for inspectable control flow, Strands for tool
              routing, AgentCore for the runtime.
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
