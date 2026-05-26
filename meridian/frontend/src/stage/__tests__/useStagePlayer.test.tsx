import { describe, expect, it, vi } from 'vitest'
import { act, renderHook, waitFor } from '@testing-library/react'
import { useStagePlayer } from '../hooks/useStagePlayer'
import type { StageSpan } from '../types'

const span = (id: string, latencyMs: number): StageSpan => ({
  id,
  kind: 'orchestration',
  system: 'orchestration',
  name: id,
  latencyMs,
})

const SPANS: StageSpan[] = [span('a', 100), span('b', 100), span('c', 100)]

/**
 * Note on timers:
 *
 * The player schedules per-span `setTimeout`s whose callbacks call
 * `setState`, which in turn re-runs the effect that schedules the *next*
 * timer. That handoff goes through React's microtask queue.
 *
 * In jsdom, mixing fake timers with React's microtask scheduling is fragile
 * (effects don't always re-run between fake-timer fires). The reliable path
 * is to use real timers with a very short total duration and `waitFor`.
 * Total real wall time per playback test is < 2s.
 */
describe('useStagePlayer', () => {
  it('starts paused at activeIndex -1 when autoPlay is false', () => {
    const { result } = renderHook(() => useStagePlayer({ spans: SPANS, autoPlay: false }))
    expect(result.current.activeIndex).toBe(-1)
    expect(result.current.isPlaying).toBe(false)
    expect(result.current.isComplete).toBe(false)
  })

  it('advances through every span and reports complete', async () => {
    const onComplete = vi.fn()
    const { result } = renderHook(() =>
      useStagePlayer({
        spans: SPANS,
        autoPlay: true,
        totalDurationMs: 300,
        minSpanMs: 30,
        onComplete,
      }),
    )

    await waitFor(
      () => {
        expect(result.current.isComplete).toBe(true)
      },
      { timeout: 2500 },
    )
    expect(result.current.activeIndex).toBe(SPANS.length - 1)
    expect(onComplete).toHaveBeenCalledTimes(1)
  })

  it('next() pauses playback and steps one span forward', () => {
    const { result } = renderHook(() => useStagePlayer({ spans: SPANS, autoPlay: false }))
    act(() => result.current.next())
    expect(result.current.activeIndex).toBe(0)
    expect(result.current.isPlaying).toBe(false)
    act(() => result.current.next())
    expect(result.current.activeIndex).toBe(1)
  })

  it('prev() steps backward but never below -1', () => {
    const { result } = renderHook(() => useStagePlayer({ spans: SPANS, autoPlay: false }))
    act(() => result.current.next())
    act(() => result.current.next())
    expect(result.current.activeIndex).toBe(1)
    act(() => result.current.prev())
    expect(result.current.activeIndex).toBe(0)
    act(() => result.current.prev())
    act(() => result.current.prev())
    expect(result.current.activeIndex).toBe(-1)
  })

  it('toggle() resumes playback from the start once the trace has finished', async () => {
    const { result } = renderHook(() =>
      useStagePlayer({ spans: SPANS, autoPlay: true, totalDurationMs: 240, minSpanMs: 20 }),
    )
    await waitFor(
      () => {
        expect(result.current.isComplete).toBe(true)
      },
      { timeout: 2500 },
    )

    act(() => result.current.toggle())
    expect(result.current.activeIndex).toBe(-1)
    expect(result.current.isPlaying).toBe(true)
  })

  it('replay() resets activeIndex to -1 and sets playing', () => {
    const { result } = renderHook(() => useStagePlayer({ spans: SPANS, autoPlay: false }))
    act(() => result.current.next())
    expect(result.current.activeIndex).toBe(0)
    act(() => result.current.replay())
    expect(result.current.activeIndex).toBe(-1)
    expect(result.current.isPlaying).toBe(true)
  })

  it('honors prefers-reduced-motion by revealing all spans immediately and pausing', () => {
    const originalMatchMedia = window.matchMedia
    window.matchMedia = (q: string) =>
      ({
        matches: true,
        media: q,
        onchange: null,
        addListener: () => {},
        removeListener: () => {},
        addEventListener: () => {},
        removeEventListener: () => {},
        dispatchEvent: () => false,
      }) as unknown as MediaQueryList

    const onComplete = vi.fn()
    const { result } = renderHook(() =>
      useStagePlayer({ spans: SPANS, autoPlay: true, onComplete }),
    )
    expect(result.current.reducedMotion).toBe(true)
    expect(result.current.activeIndex).toBe(SPANS.length - 1)
    expect(result.current.isPlaying).toBe(false)
    expect(onComplete).toHaveBeenCalledTimes(1)

    window.matchMedia = originalMatchMedia
  })
})
