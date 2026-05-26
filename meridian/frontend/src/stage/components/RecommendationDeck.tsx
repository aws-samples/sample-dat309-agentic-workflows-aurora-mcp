/**
 * RecommendationDeck — the polished output cards below the trace.
 *
 * The primary card is the headline recommendation; secondary cards make it
 * obvious that the agent considered alternatives.
 */
import type { StageRecommendation } from '../types';

interface RecommendationDeckProps {
  recommendations: StageRecommendation[];
}

export function RecommendationDeck({ recommendations }: RecommendationDeckProps) {
  return (
    <section className="ds-rec-deck" aria-label="Agent recommendations">
      {recommendations.map((rec, idx) => (
        <article key={rec.id} className={`ds-rec${rec.primary || idx === 0 ? ' is-primary' : ''}`}>
          <div className="ds-rec-hero" data-hero={rec.hero ?? 'wine'} aria-hidden="true">
            <span className="ds-rec-pill">
              {rec.primary || idx === 0 ? 'top match · held 12h' : 'alternative'}
            </span>
          </div>
          <div className="ds-rec-body">
            <div className="ds-rec-title">
              {rec.title} · {rec.nights} nights
            </div>
            <div className="ds-rec-region">{rec.region}</div>
            <div className="ds-rec-rationale">
              {rec.rationale.slice(0, 4).map((r) => (
                <span key={r}>{r}</span>
              ))}
            </div>
            <div className="ds-rec-stats">
              <span className="ds-rec-match">{rec.matchPct}% match</span>
              <span className="ds-rec-price">${rec.priceUsd.toLocaleString()}</span>
            </div>
          </div>
        </article>
      ))}
    </section>
  );
}
