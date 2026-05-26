import { describe, expect, it } from 'vitest'
import {
  DEFAULT_SCENARIO_ID,
  STAGE_SCENARIOS,
  getStageScenarioById,
} from '../data/stageScenarios'

describe('Demo Stage scenario prompts', () => {
  it('defines three keynote scenarios', () => {
    expect(STAGE_SCENARIOS).toHaveLength(3)
    const ids = STAGE_SCENARIOS.map((s) => s.id)
    expect(ids).toEqual(['wine', 'family', 'business'])
  })

  it('getStageScenarioById returns wine by default for unknown ids', () => {
    const scenario = getStageScenarioById('does-not-exist' as 'wine')
    expect(scenario.id).toBe('wine')
  })

  it('each scenario has a prompt and traveler id but no pre-baked trace', () => {
    for (const scenario of STAGE_SCENARIOS) {
      expect(scenario.prompt.length).toBeGreaterThan(10)
      expect(scenario.traveler.id).toBe('trv_meridian_demo')
      expect(scenario.spans).toEqual([])
      expect(scenario.recommendations).toEqual([])
    }
  })

  it('DEFAULT_SCENARIO_ID is wine', () => {
    expect(DEFAULT_SCENARIO_ID).toBe('wine')
  })
})
