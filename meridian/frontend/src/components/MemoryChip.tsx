/**
 * MemoryChip — short-term session + long-term Aurora facts (2026 preview)
 */
interface MemoryChipProps {
  compact?: boolean;
  onInspect?: () => void;
}

const MEMORY_FACTS = [
  '2 travelers',
  'Tokyo Oct',
  'Window seat',
  'Shellfish allergy',
];

export function MemoryChip({ compact, onInspect }: MemoryChipProps) {
  return (
    <button
      type="button"
      className={`memory-chip${compact ? ' compact' : ''}`}
      onClick={onInspect}
      title="Contextual memory — session + Aurora-backed facts"
    >
      <span className="memory-chip-label">Memory</span>
      <span className="memory-chip-facts">
        {MEMORY_FACTS.slice(0, compact ? 2 : 4).join(' · ')}
      </span>
      {!compact && <span className="memory-chip-badge">preview</span>}
    </button>
  );
}
