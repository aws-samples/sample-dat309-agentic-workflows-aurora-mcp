/**
 * HowItWorksSection — Meridian Pro Journey rail
 *
 * Replaces the four phase pillars with a horizontal four-stop journey
 * (Filters → MCP → Intent → Personal) with done / live / next states.
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
}

const steps: JourneyStep[] = [
  {
    num: '01',
    state: 'done',
    ph: 'Phase 01 · Done',
    title: 'Filters',
    serif: '',
    desc: 'Plain SQL filters on trip_packages via the RDS Data API. The fastest possible answer for an exact match.',
    chips: ['RDS Data API', 'SQL · WHERE'],
  },
  {
    num: '02',
    state: 'done',
    ph: 'Phase 02 · Done',
    title: 'MCP',
    serif: '',
    desc: 'Same queries reframed as MCP tool calls — postgres-mcp-server exposes run_query with a typed schema and dry-run.',
    chips: ['postgres-mcp-server', 'tool registry'],
  },
  {
    num: '03',
    state: 'live',
    ph: 'Phase 03 · Live',
    title: 'Intent',
    serif: '',
    desc: 'Hybrid pgvector + tsvector. Vague requests resolve to the right packages. A Strands supervisor delegates to specialists.',
    chips: ['pgvector HNSW', 'tsvector', 'Cohere v4'],
  },
  {
    num: '04',
    state: 'next',
    ph: 'Phase 04 · Next',
    title: 'Personal',
    serif: '',
    desc: 'A ConciergeOrchestrator grounds every turn in traveler_profiles and a Strands @tool memory agent. Memory in, recommendations out.',
    chips: ['Strands @tool', 'trip_interactions', 'Aurora memory'],
  },
];

const STEP_PHASE: Record<string, Phase> = {
  '01': 1,
  '02': 2,
  '03': 3,
  '04': 4,
};

export function HowItWorksSection() {
  const { openConcierge } = useAgentBridge();

  return (
    <section id="howitworks" className="mp-section">
      <FadeIn>
        <div className="mp-section-h-row">
          <div className="mp-section-h">
            <div className="mp-label-row">The four modes — a journey, not a toggle</div>
            <h2>
              From <em className="serif">filters</em> to <em className="serif">memory</em>.
            </h2>
            <p>
              Each phase climbs a rung: plain SQL filters, then MCP, then hybrid intent search,
              finally a personalized concierge that grounds every search in Aurora-stored traveler
              memory. The console below lets you scrub through all four on the same query.
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
                <div className="node">{s.state === 'done' ? '✓' : s.num.slice(-1)}</div>
                <div className="ttl">{s.title}</div>
                <div className="desc">{s.desc}</div>
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
