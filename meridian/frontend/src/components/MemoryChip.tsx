/**
 * MemoryChip — short-term session + long-term Aurora facts (Phase 4)
 */
import { useEffect, useState } from 'react';
import { fetchMemoryProfile } from '../api/client';
import type { LongTermMemoryFact } from '../types';

const DEMO_TRAVELER_ID = 'trv_meridian_demo';

interface MemoryChipProps {
  compact?: boolean;
  onInspect?: () => void;
  facts?: LongTermMemoryFact[];
}

export function MemoryChip({ compact, onInspect, facts: factsProp }: MemoryChipProps) {
  const [facts, setFacts] = useState<LongTermMemoryFact[]>(factsProp ?? []);

  useEffect(() => {
    if (factsProp?.length) {
      setFacts(factsProp);
      return;
    }
    fetchMemoryProfile(DEMO_TRAVELER_ID)
      .then((profile) => setFacts(profile.facts))
      .catch(() => setFacts([]));
  }, [factsProp]);

  const labels = facts.map((f) => f.value);

  return (
    <button
      type="button"
      className={`memory-chip${compact ? ' compact' : ''}`}
      onClick={onInspect}
      title="Contextual memory — session + Aurora-backed facts"
    >
      <span className="memory-chip-label">Memory</span>
      <span className="memory-chip-facts">
        {labels.length > 0
          ? labels.slice(0, compact ? 2 : 4).join(' · ')
          : 'Loading…'}
      </span>
      {!compact && labels.length > 0 && <span className="memory-chip-badge">Aurora</span>}
    </button>
  );
}
