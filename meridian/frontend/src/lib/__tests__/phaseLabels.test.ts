import { describe, expect, it } from 'vitest';
import { PHASE_AGENT_MODE, PHASE_EYEBROW, PHASE_JOURNEY_SUB, PHASE_PILL } from '../phaseLabels';

describe('phaseLabels', () => {
  it('labels phase 4 as Memory while preserving the production agent mode', () => {
    expect(PHASE_EYEBROW[4]).toBe('Phase 4 · Memory');
    expect(PHASE_JOURNEY_SUB[4]).toBe('Phase 04 · Memory');
    expect(PHASE_PILL[4]).toBe('Memory');
    expect(PHASE_EYEBROW[4]).not.toContain('Personal');
    expect(PHASE_AGENT_MODE[4]).toBe('Production Agent');
  });
});
