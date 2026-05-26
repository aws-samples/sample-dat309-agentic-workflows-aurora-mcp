/**
 * ConciergeResponseCard — natural-language reply card that lives at the
 * bottom of the trace hero panel.
 *
 * Reveal model:
 *   - before the model span fires → typing indicator
 *   - while the model span is active → "streaming" label + full text fading in
 *   - after the model span completes → "composed" label + full text + reasoning
 *
 * Keeping the response inside the same panel as the trace is the keynote
 * payoff: the trace literally *produces* the reply the audience sees.
 */
import type { StageRecommendation } from '../types';

type ReplyPhase = 'pending' | 'composing' | 'composed';

interface ConciergeResponseCardProps {
  reply: string;
  reasoning: string;
  phase: ReplyPhase;
  primary?: StageRecommendation | null;
}

export function ConciergeResponseCard({ reply, reasoning, phase, primary }: ConciergeResponseCardProps) {
  return (
    <div className={`ds-response phase-${phase}`} role="region" aria-label="Concierge response">
      <div className="ds-response-avatar" aria-hidden="true">
        <span>M</span>
      </div>

      <div className="ds-response-body">
        <div className="ds-response-eyebrow">
          <span className="ds-response-name">Meridian concierge</span>
          {phase === 'pending' && <span className="ds-response-status pending">awaiting trace</span>}
          {phase === 'composing' && (
            <span className="ds-response-status composing">
              <span className="ds-response-dot" /> streaming · claude.compose
            </span>
          )}
          {phase === 'composed' && (
            <span className="ds-response-status composed">composed · grounded reply</span>
          )}
        </div>

        {phase === 'pending' ? (
          <div className="ds-response-skeleton" aria-hidden="true">
            <span />
            <span />
            <span />
          </div>
        ) : (
          <p className="ds-response-text">
            {phase === 'composing' && <span className="ds-response-caret" aria-hidden="true" />}
            {reply}
          </p>
        )}

        <div className="ds-response-foot">
          <span className="ds-response-reasoning" title={reasoning}>
            <span className="ds-response-reasoning-label">trace reads</span>
            {reasoning}
          </span>
          {phase === 'composed' && primary && (
            <span className="ds-response-match">
              top match · <b>{primary.title}</b> · {primary.matchPct}% · ${primary.priceUsd.toLocaleString()}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
