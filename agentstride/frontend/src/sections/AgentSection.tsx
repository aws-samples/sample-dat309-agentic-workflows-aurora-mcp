/**
 * AgentSection - Live demo with chat and activity panel
 * Features phase selector, chat interface, and real-time activity feed
 */
import { useState, useRef, useEffect } from 'react';
import { FadeIn } from '../components/FadeIn';
import { sendChatMessage, processOrder } from '../api/client';
import type { Product, ActivityEntry, Message } from '../types';

const phaseColors = ['#3b82f6', '#a855f7', '#10b981'];
const phaseLabels = ['Phase 1 · Direct', 'Phase 2 · MCP', 'Phase 3 · Multi-Agent'];

// Phase information for educational display
const phaseInfo = {
  1: {
    name: 'Direct RDS Data API',
    description: 'Simple SQL queries via HTTP',
    capabilities: ['Category search', 'Brand filter', 'Price filter'],
    limitations: ['No semantic understanding', 'Exact keyword match only'],
    tech: 'RDS Data API → Aurora PostgreSQL',
  },
  2: {
    name: 'MCP Abstraction',
    description: 'Model Context Protocol layer',
    capabilities: ['Category search', 'Brand filter', 'Price filter', 'Tool discovery'],
    limitations: ['Still keyword-based', 'No semantic understanding'],
    tech: 'MCP Server → RDS Data API → Aurora',
  },
  3: {
    name: 'Multi-Agent + Hybrid Search',
    description: 'Semantic + Lexical combined',
    capabilities: ['Natural language queries', 'Intent understanding', 'Similarity matching'],
    limitations: [],
    tech: 'Supervisor → Agents → pgvector + tsvector',
  },
};

interface CartItem {
  product: Product;
  quantity: number;
  size?: string;
}

export function AgentSection() {
  const [phase, setPhase] = useState<1 | 2 | 3>(1);
  const [msgs, setMsgs] = useState<Message[]>([]);
  const [acts, setActs] = useState<ActivityEntry[]>([]);
  const [pendingActs, setPendingActs] = useState<ActivityEntry[]>([]);
  const [currentStep, setCurrentStep] = useState<number>(-1);
  const [input, setInput] = useState('');
  const [typing, setTyping] = useState(false);
  const [followUps, setFollowUps] = useState<string[]>([]);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [showCart, setShowCart] = useState(false);
  const [cartAnimation, setCartAnimation] = useState(false);
  const chatEnd = useRef<HTMLDivElement>(null);
  const activityTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pc = phaseColors[phase - 1];

  // Phase-specific delays (ms) - Phase 1 slower to show process, Phase 3 faster
  const phaseDelays = { 1: 600, 2: 450, 3: 350 };

  // Track previous message count to only scroll on new messages
  const prevMsgCount = useRef(0);
  const wasTyping = useRef(false);

  useEffect(() => {
    // Scroll when messages are added (not on initial load)
    if (msgs.length > prevMsgCount.current) {
      chatEnd.current?.scrollIntoView({ behavior: 'smooth' });
    }
    prevMsgCount.current = msgs.length;
  }, [msgs]);

  useEffect(() => {
    // Scroll when typing starts (user just sent a message)
    if (typing && !wasTyping.current && msgs.length > 0) {
      chatEnd.current?.scrollIntoView({ behavior: 'smooth' });
    }
    wasTyping.current = typing;
  }, [typing, msgs.length]);

  // Progressive activity reveal - shows activities one by one
  const revealActivitiesProgressively = (
    activities: ActivityEntry[],
    onComplete: () => void
  ) => {
    if (activities.length === 0) {
      onComplete();
      return;
    }

    const delay = phaseDelays[phase];
    let index = 0;

    // Show first activity immediately
    setActs([activities[0]]);
    setCurrentStep(0);
    setPendingActs(activities.slice(1));
    index = 1;

    const showNext = () => {
      if (index < activities.length) {
        const nextActivity = activities[index];
        setActs((prev) => [...prev, nextActivity]);
        setCurrentStep(index);
        setPendingActs(activities.slice(index + 1));
        index++;
        activityTimerRef.current = setTimeout(showNext, delay);
      } else {
        // All activities revealed
        setCurrentStep(-1);
        setPendingActs([]);
        onComplete();
      }
    };

    // Start revealing subsequent activities
    if (activities.length > 1) {
      activityTimerRef.current = setTimeout(showNext, delay);
    } else {
      setCurrentStep(-1);
      onComplete();
    }
  };

  const send = async () => {
    if (!input.trim() || typing) return;
    const text = input.trim();
    setInput('');
    setMsgs((p) => [...p, { role: 'user', text }]);
    setTyping(true);
    setActs([]);
    setCurrentStep(-1);
    setPendingActs([]);
    setFollowUps([]);

    // Clear any pending activity timers
    if (activityTimerRef.current) {
      clearTimeout(activityTimerRef.current);
      activityTimerRef.current = null;
    }

    try {
      const response = await sendChatMessage({
        message: text,
        phase,
      });

      // Store the response for use after activities are revealed
      const botResponse = response;

      // Progressively reveal activities, then show the response
      revealActivitiesProgressively(response.activities, () => {
        // Update follow-up suggestions
        if (botResponse.follow_ups) {
          setFollowUps(botResponse.follow_ups);
        }

        // Add bot response after activities are shown
        if (botResponse.products && botResponse.products.length > 0) {
          setMsgs((p) => [
            ...p,
            {
              role: 'bot',
              type: 'products',
              text: botResponse.message,
              products: botResponse.products,
            },
          ]);
        } else if (botResponse.order) {
          setMsgs((p) => [
            ...p,
            {
              role: 'bot',
              type: 'order',
              text: botResponse.message,
              order: botResponse.order,
            },
          ]);
        } else {
          setMsgs((p) => [
            ...p,
            {
              role: 'bot',
              type: 'text',
              text: botResponse.message,
            },
          ]);
        }
        setTyping(false);
      });
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
      setTyping(false);
    }
  };

  const switchPhase = (i: number) => {
    // Clear any pending activity timers
    if (activityTimerRef.current) {
      clearTimeout(activityTimerRef.current);
      activityTimerRef.current = null;
    }
    setPhase((i + 1) as 1 | 2 | 3);
    setMsgs([]);
    setActs([]);
    setPendingActs([]);
    setCurrentStep(-1);
    setFollowUps([]);
    setTyping(false);
  };

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (activityTimerRef.current) {
        clearTimeout(activityTimerRef.current);
      }
    };
  }, []);

  // Handle ordering a product
  const handleOrder = async (product: Product) => {
    if (typing) return;

    // Add user message indicating order intent
    setMsgs((p) => [
      ...p,
      { role: 'user', text: `Order: ${product.name}` },
    ]);
    setTyping(true);
    setActs([]);
    setCurrentStep(-1);
    setPendingActs([]);
    setFollowUps([]);

    // Clear any pending activity timers
    if (activityTimerRef.current) {
      clearTimeout(activityTimerRef.current);
      activityTimerRef.current = null;
    }

    try {
      const response = await processOrder({
        product_id: product.product_id,
        size: product.available_sizes?.includes('11') ? '11' : product.available_sizes?.[0] || undefined,
        quantity: 1,
        phase,
      });

      // Progressively reveal activities, then show the response
      revealActivitiesProgressively(response.activities, () => {
        // Add bot response with order details
        if (response.order) {
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
        setTyping(false);
      });
    } catch (error) {
      console.error('Order error:', error);
      setMsgs((p) => [
        ...p,
        {
          role: 'bot',
          type: 'text',
          text: 'Sorry, I encountered an error processing your order. Please try again.',
        },
      ]);
      setTyping(false);
    }
  };

  // Handle adding to cart
  const handleAddToCart = (product: Product) => {
    setCart((prev) => {
      const existing = prev.find((item) => item.product.product_id === product.product_id);
      if (existing) {
        return prev.map((item) =>
          item.product.product_id === product.product_id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      }
      return [...prev, { product, quantity: 1, size: product.available_sizes?.includes('11') ? '11' : product.available_sizes?.[0] }];
    });

    // Trigger cart animation
    setCartAnimation(true);
    setTimeout(() => setCartAnimation(false), 600);

    // Show confirmation in chat
    setMsgs((p) => [
      ...p,
      {
        role: 'bot',
        type: 'text',
        text: `Added **${product.name}** to your cart! You can continue shopping or checkout when ready.`,
      },
    ]);
  };

  // Calculate cart totals
  const cartTotal = cart.reduce((sum, item) => sum + item.product.price * item.quantity, 0);
  const cartCount = cart.reduce((sum, item) => sum + item.quantity, 0);

  // Phase-specific suggestions to demonstrate capabilities and limitations
  const phaseSuggestions: Record<1 | 2 | 3, { works: string[]; breaks: string[]; hint: string }> = {
    1: {
      works: ['Running shoes', 'Nike', 'Training shoes under $150'],
      breaks: ['Comfortable shoes for long runs', 'Something for marathon training'],
      hint: 'Phase 1 uses keyword matching. Try semantic queries to see limitations →',
    },
    2: {
      works: ['Fitness equipment', 'Recovery products', 'Brooks running shoes'],
      breaks: ['Lightweight breathable sneakers', 'Help with foot pain'],
      hint: 'Phase 2 uses MCP but still keyword-based. Try natural language →',
    },
    3: {
      works: ['Comfortable shoes for standing all day', 'Good for marathon training', 'Help with recovery after workouts'],
      breaks: [],
      hint: 'Phase 3 uses hybrid semantic + lexical search. Try natural language!',
    },
  };

  const currentPhaseSuggestions = phaseSuggestions[phase];

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
          <div style={{ display: 'flex', justifyContent: 'center', gap: 8, marginBottom: 16 }}>
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

          {/* Phase info panel */}
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            gap: 24,
            marginBottom: 24,
            padding: '12px 16px',
            background: `${pc}08`,
            borderRadius: 12,
            border: `1px solid ${pc}20`,
            maxWidth: 700,
            margin: '0 auto 24px',
          }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 10, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 4 }}>
                Architecture
              </div>
              <div style={{ fontSize: 11, color: '#e2e8f0', fontFamily: 'SF Mono, monospace' }}>
                {phaseInfo[phase].tech}
              </div>
            </div>
            <div style={{ width: 1, background: 'rgba(255,255,255,0.1)' }} />
            <div>
              <div style={{ fontSize: 10, color: '#10b981', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 4 }}>
                ✓ Supports
              </div>
              <div style={{ fontSize: 11, color: '#94a3b8' }}>
                {phaseInfo[phase].capabilities.join(' · ')}
              </div>
            </div>
            {phaseInfo[phase].limitations.length > 0 && (
              <>
                <div style={{ width: 1, background: 'rgba(255,255,255,0.1)' }} />
                <div>
                  <div style={{ fontSize: 10, color: '#f59e0b', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 4 }}>
                    ✗ Limitations
                  </div>
                  <div style={{ fontSize: 11, color: '#94a3b8' }}>
                    {phaseInfo[phase].limitations.join(' · ')}
                  </div>
                </div>
              </>
            )}
          </div>
        </FadeIn>

        {/* Chat + Activity */}
        <FadeIn delay={0.2}>
          <div className="agent-grid">
            {/* Chat Panel */}
            <div className="chat-panel">
              <div className="chat-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, flex: 1 }}>
                  <div
                    className="status-dot"
                    style={{ background: pc, boxShadow: `0 0 8px ${pc}` }}
                  />
                  <span className="chat-title">Shopping Assistant</span>
                </div>
              </div>

              <div className="chat-messages">
                {msgs.length === 0 && !typing && (
                  <div className="chat-empty">
                    <div style={{ fontSize: 36, opacity: 0.3 }}>💬</div>
                    <p style={{ fontSize: 12, color: '#64748b', marginBottom: 12 }}>
                      {currentPhaseSuggestions.hint}
                    </p>

                    {/* Queries that work in this phase */}
                    <div style={{ marginBottom: 12 }}>
                      <div style={{ fontSize: 10, color: '#10b981', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                        ✓ Works in Phase {phase}
                      </div>
                      <div className="chat-suggestions">
                        {currentPhaseSuggestions.works.map((s) => (
                          <button
                            key={s}
                            onClick={() => setInput(s)}
                            className="suggestion-btn"
                            style={{
                              '--phase-color': pc,
                              border: `1px solid ${pc}40`,
                            } as React.CSSProperties}
                          >
                            {s}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Queries that break in this phase (show limitations) */}
                    {currentPhaseSuggestions.breaks.length > 0 && (
                      <div>
                        <div style={{ fontSize: 10, color: '#f59e0b', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                          ⚠ Try these to see limitations
                        </div>
                        <div className="chat-suggestions">
                          {currentPhaseSuggestions.breaks.map((s) => (
                            <button
                              key={s}
                              onClick={() => setInput(s)}
                              className="suggestion-btn"
                              style={{
                                '--phase-color': '#f59e0b',
                                border: '1px solid rgba(245, 158, 11, 0.3)',
                                background: 'rgba(245, 158, 11, 0.05)',
                              } as React.CSSProperties}
                            >
                              {s}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
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
                          <div key={j} className="product-result" style={{ position: 'relative' }}>
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
                                style={{ color: pc, background: `${pc}15`, marginRight: 8 }}
                              >
                                {(pr.similarity * 100).toFixed(0)}%
                              </span>
                            )}
                            <div style={{ display: 'flex', gap: 6 }}>
                              <button
                                onClick={() => handleAddToCart(pr)}
                                disabled={typing}
                                style={{
                                  padding: '6px 10px',
                                  fontSize: 10,
                                  fontWeight: 600,
                                  background: 'transparent',
                                  border: `1px solid ${pc}50`,
                                  borderRadius: 6,
                                  color: pc,
                                  cursor: typing ? 'not-allowed' : 'pointer',
                                  opacity: typing ? 0.5 : 1,
                                  transition: 'all 0.2s ease',
                                  whiteSpace: 'nowrap',
                                }}
                                onMouseEnter={(e) => {
                                  if (!typing) {
                                    e.currentTarget.style.background = `${pc}15`;
                                    e.currentTarget.style.borderColor = pc;
                                  }
                                }}
                                onMouseLeave={(e) => {
                                  e.currentTarget.style.background = 'transparent';
                                  e.currentTarget.style.borderColor = `${pc}50`;
                                }}
                              >
                                + Cart
                              </button>
                              <button
                                onClick={() => handleOrder(pr)}
                                disabled={typing}
                                style={{
                                  padding: '6px 10px',
                                  fontSize: 10,
                                  fontWeight: 600,
                                  background: pc,
                                  border: 'none',
                                  borderRadius: 6,
                                  color: '#fff',
                                  cursor: typing ? 'not-allowed' : 'pointer',
                                  opacity: typing ? 0.5 : 1,
                                  transition: 'all 0.2s ease',
                                  whiteSpace: 'nowrap',
                                }}
                                onMouseEnter={(e) => {
                                  if (!typing) e.currentTarget.style.transform = 'scale(1.05)';
                                }}
                                onMouseLeave={(e) => {
                                  e.currentTarget.style.transform = 'scale(1)';
                                }}
                              >
                                Buy Now
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : m.type === 'order' && m.order ? (
                      <div className="order-response">
                        <div style={{
                          background: `${pc}10`,
                          border: `1px solid ${pc}30`,
                          borderRadius: 12,
                          padding: 16,
                          marginBottom: 8,
                        }}>
                          <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 8,
                            marginBottom: 12,
                          }}>
                            <span style={{ fontSize: 20 }}>✅</span>
                            <span style={{ fontWeight: 600, color: pc }}>Order Confirmed</span>
                          </div>
                          <div style={{ fontSize: 12, color: '#94a3b8', marginBottom: 8 }}>
                            Order #{m.order.order_id}
                          </div>
                          {m.order.items.map((item, idx) => (
                            <div key={idx} style={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              fontSize: 13,
                              marginBottom: 4,
                            }}>
                              <span>{item.name} {item.size && `(${item.size})`}</span>
                              <span>${item.unit_price.toFixed(2)}</span>
                            </div>
                          ))}
                          <div style={{
                            borderTop: '1px solid rgba(255,255,255,0.1)',
                            marginTop: 8,
                            paddingTop: 8,
                            fontSize: 12,
                          }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 2 }}>
                              <span style={{ color: '#64748b' }}>Subtotal</span>
                              <span>${m.order.subtotal.toFixed(2)}</span>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 2 }}>
                              <span style={{ color: '#64748b' }}>Tax</span>
                              <span>${m.order.tax.toFixed(2)}</span>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                              <span style={{ color: '#64748b' }}>Shipping</span>
                              <span>{m.order.shipping === 0 ? 'FREE' : `$${m.order.shipping.toFixed(2)}`}</span>
                            </div>
                            <div style={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              fontWeight: 600,
                              fontSize: 14,
                              color: pc,
                            }}>
                              <span>Total</span>
                              <span>${m.order.total.toFixed(2)}</span>
                            </div>
                          </div>
                          {m.order.estimated_delivery && (
                            <div style={{
                              marginTop: 12,
                              padding: '8px 12px',
                              background: 'rgba(255,255,255,0.05)',
                              borderRadius: 8,
                              fontSize: 12,
                            }}>
                              <span style={{ color: '#64748b' }}>📦 Estimated delivery: </span>
                              <span style={{ fontWeight: 500 }}>{m.order.estimated_delivery}</span>
                            </div>
                          )}
                        </div>
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
                
                {/* Follow-up suggestions */}
                {!typing && followUps.length > 0 && (
                  <div className="follow-ups" style={{ marginTop: 12, marginBottom: 8 }}>
                    <div style={{ 
                      fontSize: 11, 
                      color: '#64748b', 
                      marginBottom: 8,
                      textTransform: 'uppercase',
                      letterSpacing: '0.5px'
                    }}>
                      Try asking:
                    </div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                      {followUps.map((fu, i) => (
                        <button
                          key={i}
                          onClick={() => setInput(fu)}
                          className="follow-up-btn"
                          style={{
                            padding: '6px 12px',
                            fontSize: 12,
                            background: `${pc}10`,
                            border: `1px solid ${pc}30`,
                            borderRadius: 16,
                            color: pc,
                            cursor: 'pointer',
                            transition: 'all 0.2s ease',
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.background = `${pc}20`;
                            e.currentTarget.style.borderColor = `${pc}50`;
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.background = `${pc}10`;
                            e.currentTarget.style.borderColor = `${pc}30`;
                          }}
                        >
                          {fu}
                        </button>
                      ))}
                    </div>
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
                      background: currentStep >= 0 ? pc : acts.length > 0 ? '#10b981' : '#334155',
                      boxShadow: currentStep >= 0 ? `0 0 12px ${pc}` : acts.length > 0 ? '0 0 8px #10b981' : 'none',
                      animation: currentStep >= 0 ? 'pulseGlow 1.5s ease-in-out infinite' : 'none',
                    }}
                  />
                  <span className="activity-title">Agent Activity</span>
                </div>
                <span className="activity-count" style={{ color: currentStep >= 0 ? pc : undefined }}>
                  {currentStep >= 0
                    ? `step ${currentStep + 1}/${acts.length + pendingActs.length}`
                    : acts.length > 0
                      ? `${acts.length} ops`
                      : 'idle'}
                </span>
              </div>

              <div className="activity-feed">
                {acts.length === 0 && currentStep < 0 && (
                  <div className="activity-empty">
                    <div style={{ fontSize: 28 }}>⊘</div>
                    <div>Waiting for activity</div>
                  </div>
                )}

                {/* Revealed activities */}
                {acts.map((a, i) => {
                  const isCurrentStep = i === currentStep;
                  return (
                    <div
                      key={a.id || i}
                      className="activity-item"
                      style={{
                        borderLeft: isCurrentStep ? `3px solid ${pc}` : '3px solid transparent',
                        background: isCurrentStep ? `${pc}08` : undefined,
                        transition: 'all 0.3s ease',
                      }}
                    >
                      <div className="activity-item-header">
                        <span style={{
                          fontSize: 14,
                          animation: isCurrentStep ? 'stepPulse 1s ease-in-out infinite' : 'none',
                        }}>
                          {a.activity_type === 'search' ? '🔍' :
                           a.activity_type === 'embedding' ? '🧠' :
                           a.activity_type === 'mcp' ? '🔌' :
                           a.activity_type === 'database' ? '🗄️' :
                           a.activity_type === 'reasoning' ? '💭' :
                           a.activity_type === 'result' ? '✅' :
                           a.activity_type === 'error' ? '❌' :
                           a.activity_type === 'inventory' ? '📦' :
                           a.activity_type === 'order' ? '💳' : '⚡'}
                        </span>
                        <div style={{ flex: 1 }}>
                          <div className="activity-label" style={{ color: isCurrentStep ? pc : undefined }}>
                            {a.title}
                          </div>
                          <div className="activity-agent" style={{ color: pc }}>
                            {a.agent_name || `Phase${phase}Agent`}
                          </div>
                          {a.agent_file && (
                            <div style={{
                              fontSize: 9,
                              fontFamily: 'SF Mono, monospace',
                              color: '#475569',
                              marginTop: 2,
                            }}>
                              {a.agent_file}
                            </div>
                          )}
                        </div>
                        {a.execution_time_ms ? (
                          <span className="activity-time">{a.execution_time_ms}ms</span>
                        ) : isCurrentStep ? (
                          <span className="activity-time" style={{ color: pc }}>...</span>
                        ) : null}
                      </div>
                      {a.details && (
                        <div className="activity-detail" style={{ borderLeftColor: `${pc}30` }}>
                          {a.details}
                        </div>
                      )}
                      {a.sql_query && (
                        <div className="activity-sql" style={{
                          borderLeftColor: `${pc}30`,
                          marginTop: 4,
                          paddingLeft: 8,
                          borderLeft: `2px solid ${pc}20`,
                          fontSize: 10,
                          fontFamily: 'SF Mono, monospace',
                          color: '#64748b',
                          whiteSpace: 'nowrap',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis'
                        }}>
                          {a.sql_query}
                        </div>
                      )}
                    </div>
                  );
                })}

                {/* Pending activities (shown as placeholders) */}
                {pendingActs.map((a, i) => (
                  <div
                    key={`pending-${i}`}
                    className="activity-item"
                    style={{
                      opacity: 0.4,
                      borderLeft: '3px solid transparent',
                    }}
                  >
                    <div className="activity-item-header">
                      <span style={{ fontSize: 14, filter: 'grayscale(1)' }}>
                        {a.activity_type === 'search' ? '🔍' :
                         a.activity_type === 'embedding' ? '🧠' :
                         a.activity_type === 'mcp' ? '🔌' :
                         a.activity_type === 'database' ? '🗄️' :
                         a.activity_type === 'reasoning' ? '💭' :
                         a.activity_type === 'result' ? '✅' :
                         a.activity_type === 'error' ? '❌' :
                         a.activity_type === 'inventory' ? '📦' :
                         a.activity_type === 'order' ? '💳' : '⚡'}
                      </span>
                      <div style={{ flex: 1 }}>
                        <div className="activity-label" style={{ color: '#475569' }}>
                          {a.title}
                        </div>
                        <div className="activity-agent" style={{ color: '#334155' }}>
                          {a.agent_name || `Phase${phase}Agent`}
                        </div>
                        {a.agent_file && (
                          <div style={{
                            fontSize: 9,
                            fontFamily: 'SF Mono, monospace',
                            color: '#334155',
                            marginTop: 2,
                          }}>
                            {a.agent_file}
                          </div>
                        )}
                      </div>
                      <span className="activity-time" style={{ color: '#334155' }}>—</span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="activity-stats">
                <span>
                  <span style={{ color: pc }}>●</span> Phase {phase}
                </span>
                <span>{acts.length > 0 ? `${acts.reduce((sum, a) => sum + (a.execution_time_ms || 0), 0)}ms` : '—'}</span>
                <span>{acts.length + pendingActs.length} steps</span>
                <span>1024d vectors</span>
              </div>
            </div>
          </div>
        </FadeIn>
      </div>
    </section>
  );
}
