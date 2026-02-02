/**
 * AgentSection - Live demo with chat and activity panel
 * Features phase selector, chat interface, and real-time activity feed
 */
import { useState, useRef, useEffect } from 'react';
import { FadeIn } from '../components/FadeIn';
import { sendChatMessage } from '../api/client';
import type { Product, ActivityEntry, Message } from '../types';

const phaseColors = ['#3b82f6', '#a855f7', '#10b981'];
const phaseLabels = ['Phase 1 · Direct', 'Phase 2 · MCP', 'Phase 3 · Multi-Agent'];

export function AgentSection() {
  const [phase, setPhase] = useState<1 | 2 | 3>(1);
  const [msgs, setMsgs] = useState<Message[]>([]);
  const [acts, setActs] = useState<ActivityEntry[]>([]);
  const [input, setInput] = useState('');
  const [typing, setTyping] = useState(false);
  const chatEnd = useRef<HTMLDivElement>(null);
  const pc = phaseColors[phase - 1];

  useEffect(() => {
    chatEnd.current?.scrollIntoView({ behavior: 'smooth' });
  }, [msgs, typing]);

  const send = async () => {
    if (!input.trim() || typing) return;
    const text = input.trim();
    setInput('');
    setMsgs((p) => [...p, { role: 'user', text }]);
    setTyping(true);
    setActs([]);

    try {
      const response = await sendChatMessage({
        message: text,
        phase,
      });

      // Update activities as they come in
      setActs(response.activities);

      // Add bot response
      if (response.products && response.products.length > 0) {
        setMsgs((p) => [
          ...p,
          {
            role: 'bot',
            type: 'products',
            text: response.message,
            products: response.products,
          },
        ]);
      } else if (response.order) {
        setMsgs((p) => [
          ...p,
          {
            role: 'bot',
            type: 'order',
            text: response.message,
            order: response.order,
          },
        ]);
      } else {
        setMsgs((p) => [
          ...p,
          {
            role: 'bot',
            type: 'text',
            text: response.message,
          },
        ]);
      }
    } catch (error) {
      console.error('Chat error:', error);
      setMsgs((p) => [
        ...p,
        {
          role: 'bot',
          type: 'text',
          text: 'Sorry, I encountered an error. Please try again.',
        },
      ]);
    } finally {
      setTyping(false);
    }
  };

  const switchPhase = (i: number) => {
    setPhase((i + 1) as 1 | 2 | 3);
    setMsgs([]);
    setActs([]);
    setTyping(false);
  };

  const suggestions = ['Running shoes', 'Trail shoes under $150', 'Show me fitness equipment'];

  return (
    <section
      id="agent"
      style={{
        position: 'relative',
        padding: '120px 40px 80px',
        background: '#060a14',
      }}
    >
      {/* Top accent line */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: 1,
          background: 'linear-gradient(90deg, transparent, rgba(16,185,129,0.3), transparent)',
        }}
      />

      <div style={{ maxWidth: 1200, margin: '0 auto' }}>
        {/* Header */}
        <FadeIn>
          <div style={{ textAlign: 'center', marginBottom: 48 }}>
            <span className="section-label" style={{ color: '#10b981' }}>
              Live Demo
            </span>
            <h2 className="section-headline">Talk to the agent.</h2>
          </div>
        </FadeIn>

        {/* Phase pills */}
        <FadeIn delay={0.1}>
          <div style={{ display: 'flex', justifyContent: 'center', gap: 8, marginBottom: 32 }}>
            {phaseLabels.map((label, i) => (
              <button
                key={i}
                onClick={() => switchPhase(i)}
                className="phase-pill"
                style={{
                  border:
                    phase === i + 1
                      ? `1.5px solid ${phaseColors[i]}40`
                      : '1.5px solid rgba(255,255,255,0.06)',
                  background: phase === i + 1 ? `${phaseColors[i]}12` : 'rgba(255,255,255,0.02)',
                  color: phase === i + 1 ? phaseColors[i] : '#475569',
                }}
              >
                {label}
              </button>
            ))}
          </div>
        </FadeIn>

        {/* Chat + Activity */}
        <FadeIn delay={0.2}>
          <div className="agent-grid">
            {/* Chat Panel */}
            <div className="chat-panel">
              <div className="chat-header">
                <div
                  className="status-dot"
                  style={{ background: pc, boxShadow: `0 0 8px ${pc}` }}
                />
                <span className="chat-title">Shopping Assistant</span>
              </div>

              <div className="chat-messages">
                {msgs.length === 0 && !typing && (
                  <div className="chat-empty">
                    <div style={{ fontSize: 36, opacity: 0.3 }}>💬</div>
                    <p>Try "Show me comfortable running shoes for marathon training"</p>
                    <div className="chat-suggestions">
                      {suggestions.map((s) => (
                        <button
                          key={s}
                          onClick={() => setInput(s)}
                          className="suggestion-btn"
                          style={
                            {
                              '--phase-color': pc,
                            } as React.CSSProperties
                          }
                        >
                          {s}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {msgs.map((m, i) => (
                  <div
                    key={i}
                    className={`message ${m.role}`}
                    style={m.role === 'user' ? { background: pc } : undefined}
                  >
                    {m.role === 'user' ? (
                      m.text
                    ) : m.type === 'products' && m.products ? (
                      <div className="products-response">
                        <p className="products-intro">{m.text}</p>
                        {m.products.map((pr: Product, j: number) => (
                          <div key={j} className="product-result">
                            <img
                              src={pr.image_url}
                              alt={pr.name}
                              style={{
                                width: 48,
                                height: 48,
                                borderRadius: 8,
                                objectFit: 'cover',
                              }}
                              onError={(e) => {
                                (e.target as HTMLImageElement).src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48"><rect fill="%231e293b" width="48" height="48"/></svg>';
                              }}
                            />
                            <div style={{ flex: 1 }}>
                              <div className="product-result-name">{pr.name}</div>
                              <div className="product-result-meta">
                                ${pr.price.toFixed(2)} · {pr.brand}
                              </div>
                            </div>
                            {pr.similarity && (
                              <span
                                className="similarity-badge"
                                style={{ color: pc, background: `${pc}15` }}
                              >
                                {(pr.similarity * 100).toFixed(0)}%
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      m.text
                    )}
                  </div>
                ))}

                {typing && (
                  <div className="typing-indicator">
                    {[0, 1, 2].map((k) => (
                      <div
                        key={k}
                        className="typing-dot"
                        style={{
                          background: pc,
                          animationDelay: `${k * 0.15}s`,
                        }}
                      />
                    ))}
                  </div>
                )}
                <div ref={chatEnd} />
              </div>

              <div className="chat-input-bar">
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && send()}
                  placeholder="Ask about products..."
                  className="chat-input"
                  style={
                    {
                      '--phase-color': pc,
                    } as React.CSSProperties
                  }
                />
                <button
                  onClick={send}
                  className="send-btn"
                  style={{ background: pc, boxShadow: `0 4px 15px ${pc}30` }}
                >
                  ↑
                </button>
              </div>
            </div>

            {/* Activity Panel */}
            <div className="activity-panel">
              <div className="activity-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <div
                    className="status-dot"
                    style={{
                      background: acts.length > 0 ? '#10b981' : '#334155',
                      boxShadow: acts.length > 0 ? '0 0 8px #10b981' : 'none',
                    }}
                  />
                  <span className="activity-title">Agent Activity</span>
                </div>
                <span className="activity-count">{acts.length > 0 ? `${acts.length} ops` : 'idle'}</span>
              </div>

              <div className="activity-feed">
                {acts.length === 0 && (
                  <div className="activity-empty">
                    <div style={{ fontSize: 28 }}>⊘</div>
                    <div>Waiting for activity</div>
                  </div>
                )}

                {acts.map((a, i) => (
                  <div key={i} className="activity-item">
                    <div className="activity-item-header">
                      <span style={{ fontSize: 14 }}>
                        {a.activity_type === 'search' ? '🔍' : a.activity_type === 'embedding' ? '🧠' : '⚡'}
                      </span>
                      <div style={{ flex: 1 }}>
                        <div className="activity-label">{a.title}</div>
                        <div className="activity-agent" style={{ color: pc }}>
                          {a.agent_name || `Phase${phase}Agent`}
                        </div>
                      </div>
                      {a.execution_time_ms && (
                        <span className="activity-time">{a.execution_time_ms}ms</span>
                      )}
                    </div>
                    {a.details && (
                      <div className="activity-detail" style={{ borderLeftColor: `${pc}30` }}>
                        {a.details}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              <div className="activity-stats">
                <span>
                  <span style={{ color: pc }}>●</span> Phase {phase}
                </span>
                <span>{acts.length > 0 ? `${acts.reduce((sum, a) => sum + (a.execution_time_ms || 0), 0)}ms` : '—'}</span>
                <span>{acts.length} tools</span>
                <span>1024d</span>
              </div>
            </div>
          </div>
        </FadeIn>
      </div>
    </section>
  );
}
