/**
 * ProConciergeResponse — light-theme concierge reply card (Daylight Studio).
 *
 * Same reveal model as the Demo Stage kiosk: pending → composing → composed,
 * with trace reasoning and top-match callout.
 */
import type { Product } from '../types';

type ReplyPhase = 'pending' | 'composing' | 'composed';

interface ProConciergeResponseProps {
  reply: string;
  reasoning: string;
  phase: ReplyPhase;
  primaryProduct?: Product | null;
  visible?: boolean;
}

export function ProConciergeResponse({
  reply,
  reasoning,
  phase,
  primaryProduct,
  visible = true,
}: ProConciergeResponseProps) {
  if (!visible) return null;

  return (
    <div className={`mp-response phase-${phase}`} role="region" aria-label="Concierge response">
      <div className="mp-response-avatar" aria-hidden="true">
        <span>M</span>
      </div>
      <div className="mp-response-body">
        <div className="mp-response-eyebrow">
          <span className="mp-response-name">Meridian concierge</span>
          {phase === 'pending' && (
            <span className="mp-response-status pending">awaiting trace</span>
          )}
          {phase === 'composing' && (
            <span className="mp-response-status composing">
              <span className="mp-response-dot" /> streaming · grounded compose
            </span>
          )}
          {phase === 'composed' && (
            <span className="mp-response-status composed">composed · grounded reply</span>
          )}
        </div>

        {phase === 'pending' ? (
          <div className="mp-response-skeleton" aria-hidden="true">
            <span /><span /><span />
          </div>
        ) : (
          <p className="mp-response-text">
            {phase === 'composing' && <span className="mp-response-caret" aria-hidden="true" />}
            {reply}
          </p>
        )}

        <div className="mp-response-foot">
          <span className="mp-response-reasoning" title={reasoning}>
            <span className="mp-response-reasoning-label">trace reads</span>
            {reasoning}
          </span>
          {phase === 'composed' && primaryProduct && (
            <span className="mp-response-match">
              top match · <b>{primaryProduct.name}</b>
              {primaryProduct.similarity != null && (
                <> · {(primaryProduct.similarity * 100).toFixed(0)}%</>
              )}
              {' · '}${Math.round(primaryProduct.price).toLocaleString()}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
