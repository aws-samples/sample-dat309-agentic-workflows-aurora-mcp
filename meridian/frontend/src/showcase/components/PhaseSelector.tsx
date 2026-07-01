import type { MeridianShowcaseState } from '../hooks/useMeridianShowcase';
import { SHOWCASE_PHASES } from '../lib/showcaseAdapters';

export function PhaseSelector({ state, compact = false }: { state: MeridianShowcaseState; compact?: boolean }) {
  return (
    <div className={`mds-phase-selector-wrap${compact ? ' is-compact' : ''}`}>
      <div className="mds-phase-selector" role="tablist" aria-label="Planning phase">
        {SHOWCASE_PHASES.map((phase) => (
          <button
            key={phase.label}
            type="button"
            role="tab"
            aria-selected={state.selectedPhase === phase.phase}
            className={state.selectedPhase === phase.phase ? 'is-active' : ''}
            onClick={() => state.setSelectedPhase(phase.phase)}
            title={`${phase.description}. ${phase.proofPoint}.`}
          >
            <span>{phase.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
