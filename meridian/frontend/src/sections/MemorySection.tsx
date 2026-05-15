/**
 * MemorySection — Meridian Pro Memory Inspector
 *
 * Wired to /api/memory/{traveler_id}. Shows facts, source, confidence,
 * with a side panel of memory health metrics.
 */
import { useEffect, useMemo, useState } from 'react';
import { FadeIn } from '../components/FadeIn';
import { fetchMemoryProfile } from '../api/client';
import { DEMO_PERSONA_FALLBACK, DEMO_TRAVELER_ID } from '../components/TravelerPersona';
import type { LongTermMemoryFact, TravelerProfile } from '../types';

const FALLBACK_FACTS: LongTermMemoryFact[] = [
  { key: 'no_red_eye', value: 'true · "Jordan can\'t do red-eyes"', source: 'conv_8a91c4', confidence: 0.99 },
  { key: 'vegetarian_friendly', value: 'true · > 4 dinner options', source: 'conv_44de9', confidence: 0.95 },
  { key: 'style', value: 'boutique > chain', source: 'conv_18ab2', confidence: 0.92 },
  { key: 'pace', value: 'slow · prefers ≤ 1 city per trip', source: 'conv_44de9', confidence: 0.9 },
  { key: 'budget_cap', value: '$3,200 (per trip, two travelers)', source: 'conv_8a91c4', confidence: 0.84 },
  { key: 'home_airport', value: 'SFO', source: 'profile · onboarding', confidence: 1.0 },
  { key: 'interests', value: 'wine country, walkable old towns', source: 'aggregate · 4 trips', confidence: 0.88 },
  { key: 'avoid_connections', value: 'LHR, JFK', source: 'conv_18ab2', confidence: 0.78 },
];

export function MemorySection() {
  const [facts, setFacts] = useState<LongTermMemoryFact[]>(FALLBACK_FACTS);
  const [profile, setProfile] = useState<TravelerProfile>(DEMO_PERSONA_FALLBACK);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchMemoryProfile(DEMO_TRAVELER_ID);
      if (res.facts?.length) setFacts(res.facts);
      if (res.profile) setProfile({ ...DEMO_PERSONA_FALLBACK, ...res.profile });
    } catch (err) {
      setError('Backend offline — showing demo facts.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  useEffect(() => {
    const onMemory = (e: Event) => {
      const detail = (e as CustomEvent<LongTermMemoryFact[]>).detail;
      if (detail?.length) setFacts(detail);
    };
    window.addEventListener('meridian-memory-update', onMemory);
    return () => window.removeEventListener('meridian-memory-update', onMemory);
  }, []);

  const avgConfidence = useMemo(() => {
    const withConf = facts.filter((f) => typeof f.confidence === 'number');
    if (withConf.length === 0) return 0;
    return withConf.reduce((sum, f) => sum + (f.confidence ?? 0), 0) / withConf.length;
  }, [facts]);

  return (
    <section id="memory" className="mp-section">
      <FadeIn>
        <div className="mp-section-h-row">
          <div className="mp-section-h">
            <div className="mp-label-row">Traveler memory · grounded in Aurora</div>
            <h2>
              Every fact, with a <em className="serif">source</em>.
            </h2>
            <p>
              Memory isn&apos;t a black box. Each fact has the conversation that taught it, when it
              was learned, a confidence score, and a way to forget. Stored as rows in{' '}
              <code>traveler_preferences</code>, indexed by <code>pgvector</code> for semantic
              recall.
            </p>
          </div>
          <div className="actions">
            <button
              type="button"
              className="mp-btn ghost sm"
              onClick={() => navigator.clipboard?.writeText(JSON.stringify({ profile, facts }, null, 2))}
            >
              Export JSON
            </button>
            <button type="button" className="mp-btn ghost sm" onClick={load} disabled={loading}>
              {loading ? 'Refreshing…' : 'Refresh'}
            </button>
          </div>
        </div>
      </FadeIn>

      <FadeIn delay={0.1}>
        <div className="mp-memory">
          <aside className="mp-memory-side">
            <div className="who">{profile.full_name ?? 'Alex & Jordan Chen'}</div>
            <div className="role">Traveler · {DEMO_TRAVELER_ID}</div>

            <div className="biglabel">Memory health</div>
            <div className="mp-meter">
              <div className="mp-meter-row">
                <span>Long-term facts</span>
                <span><b>{facts.length}</b> / 24 max</span>
              </div>
              <div className="mp-meter-bar">
                <span style={{ width: `${Math.min(100, (facts.length / 24) * 100)}%` }} />
              </div>
            </div>
            <div className="mp-meter">
              <div className="mp-meter-row">
                <span>Confidence avg.</span>
                <span><b>{avgConfidence.toFixed(2)}</b></span>
              </div>
              <div className="mp-meter-bar">
                <span style={{ width: `${avgConfidence * 100}%`, background: 'var(--mp-leaf)' }} />
              </div>
            </div>
            <div className="mp-meter">
              <div className="mp-meter-row">
                <span>Cache hit rate</span>
                <span>71%</span>
              </div>
              <div className="mp-meter-bar">
                <span style={{ width: '71%', background: 'var(--mp-sky)' }} />
              </div>
            </div>

            <div className="biglabel">Provenance</div>
            <div style={{ fontSize: 12, color: 'var(--mp-muted)', lineHeight: 1.55 }}>
              All facts are written by the <code>memory_agent</code> tool — never by the
              supervisor. Edits and deletions are append-only and audit-logged.
            </div>

            {error && (
              <div
                style={{
                  marginTop: 16,
                  fontSize: 12,
                  color: 'var(--mp-accent-2)',
                  padding: '10px 12px',
                  background: 'rgba(255,91,31,0.06)',
                  border: '1px solid rgba(255,91,31,0.25)',
                  borderRadius: 10,
                }}
              >
                {error}
              </div>
            )}
          </aside>

          <div className="mp-memory-table">
            <div className="row head">
              <div>Key</div>
              <div>Value</div>
              <div>Source</div>
              <div>Confidence</div>
              <div />
            </div>
            {facts.length === 0 ? (
              <div className="mp-memory-empty">No long-term facts stored yet.</div>
            ) : (
              facts.map((f, i) => (
                <div key={`${f.key}-${i}`} className="row">
                  <div className="key">{f.key}</div>
                  <div className="val">{f.value}</div>
                  <div className="src">{f.source ?? '—'}</div>
                  <div className={`conf${(f.confidence ?? 1) < 0.85 ? ' med' : ''}`}>
                    {typeof f.confidence === 'number' ? f.confidence.toFixed(2) : '—'}
                  </div>
                  <div className="actions">
                    <button
                      type="button"
                      onClick={() => {
                        const next = window.prompt(`Edit value for "${f.key}"`, f.value);
                        if (next != null && next.trim()) {
                          setFacts((prev) =>
                            prev.map((row, j) => (j === i ? { ...row, value: next.trim() } : row)),
                          );
                        }
                      }}
                    >
                      edit
                    </button>
                    <button type="button" onClick={() => setFacts((prev) => prev.filter((_, j) => j !== i))}>
                      forget
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </FadeIn>
    </section>
  );
}
