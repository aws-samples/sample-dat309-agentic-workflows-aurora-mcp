/**
 * AgentSection - Live demo with chat and activity panel
 * Features phase selector, chat interface, and real-time activity feed
 */
import { useState, useRef, useEffect } from 'react';
import { FadeIn } from '../components/FadeIn';
import { MemoryChip } from '../components/MemoryChip';
import { TraceSpan } from '../components/TraceSpan';
import { ProductThumb } from '../components/ProductThumb';
import { enrichTraceActivities } from '../utils/traceTelemetry';
import { sendChatMessage, processOrder } from '../api/client';
import type { Product, ActivityEntry, Message, Phase } from '../types';

const phaseColors = ['#3b82f6', '#a855f7', '#10b981', '#ff5b1f'];
const phaseLabels = [
  'Phase 1 · Keywords',
  'Phase 2 · MCP',
  'Phase 3 · Semantic',
  'Phase 4 · Memory',
];

// Phase information for educational display
const phaseInfo: Record<Phase, {
  name: string;
  beat: string;
  description: string;
  capabilities: string[];
  limitations: string[];
  tech: string;
}> = {
  1: {
    name: 'Keyword concierge',
    beat: 'Exact trip type & operator lookup — no natural language yet.',
    description: 'Hardcoded SQL via RDS Data API',
    capabilities: ['Trip-type filter', 'Operator filter', 'Price filter'],
    limitations: ['No semantic understanding', 'Exact keyword match only'],
    tech: 'RDS Data API → Aurora PostgreSQL',
  },
  2: {
    name: 'MCP discovery',
    beat: 'Tools discovered at runtime — still keyword search underneath.',
    description: 'Model Context Protocol tool layer',
    capabilities: ['Trip-type filter', 'Operator filter', 'Price filter', 'MCP tool discovery'],
    limitations: ['Still keyword-based', 'No vector search'],
    tech: 'MCP Server → RDS Data API → Aurora',
  },
  3: {
    name: 'Specialist team',
    beat: 'Hybrid pgvector search — vague travel intent maps to real packages.',
    description: 'Supervisor + semantic retrieval',
    capabilities: ['Natural language', 'Supervisor routing', 'Hybrid pgvector search'],
    limitations: ['No durable memory', 'Stateless across sessions'],
    tech: 'Supervisor → [Search · Availability · Booking] → Aurora',
  },
  4: {
    name: 'Partner runtime',
    beat: 'Remembers party size, dates, and dietary needs before every turn.',
    description: 'AgentCore + Aurora memory.facts',
    capabilities: [
      'Short- & long-term memory',
      'AgentCore session + trace',
      'Multi-turn travel planning',
      'Plan → confirm → book',
    ],
    limitations: [],
    tech: 'AgentCore · Memory · LangGraph · MCP · Aurora',
  },
};

interface CartItem {
  product: Product;
  quantity: number;
  size?: string;
}

export function AgentSection() {
  const [phase, setPhase] = useState<Phase>(1);
  const [msgs, setMsgs] = useState<Message[]>([]);
  const [acts, setActs] = useState<ActivityEntry[]>([]);
  const [pendingActs, setPendingActs] = useState<ActivityEntry[]>([]);
  const [currentStep, setCurrentStep] = useState<number>(-1);
  const [input, setInput] = useState('');
  const [typing, setTyping] = useState(false);
  const [followUps, setFollowUps] = useState<string[]>([]);
  const [phaseTransition, setPhaseTransition] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');
  const [traceId, setTraceId] = useState<string | null>(null);
  // Cart state - setCart is used but cart value not read directly (used in callback)
  const [, setCart] = useState<CartItem[]>([]);
  const chatEnd = useRef<HTMLDivElement>(null);
  const activityTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pc = phaseColors[phase - 1];

  const ensureTraceId = (): string => {
    if (traceId) return traceId;
    const id = `tr_${Math.random().toString(36).slice(2, 8)}`;
    setTraceId(id);
    return id;
  };

  // Check backend connection on mount
  useEffect(() => {
    const checkConnection = async () => {
      try {
        const response = await fetch('http://localhost:8000/health');
        setConnectionStatus(response.ok ? 'connected' : 'disconnected');
      } catch {
        setConnectionStatus('disconnected');
      }
    };
    checkConnection();
    // Re-check every 30 seconds
    const interval = setInterval(checkConnection, 30000);
    return () => clearInterval(interval);
  }, []);

  // Phase-specific delays (ms) - Phase 1 slower to show process, Phase 3 faster
  const phaseDelays: Record<Phase, number> = { 1: 600, 2: 450, 3: 350, 4: 300 };

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
    const userMsg: Message = { role: 'user', text };
    const history = [...msgs, userMsg];
    setMsgs((p) => [...p, userMsg]);
    setTyping(true);
    setActs([]);
    setCurrentStep(-1);
    setPendingActs([]);
    setFollowUps([]);

    const tid = ensureTraceId();

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
      revealActivitiesProgressively(
        enrichTraceActivities(phase, text, response.activities, tid, history, {
          productCount: botResponse.products?.length,
        }),
        () => {
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
      setConnectionStatus('disconnected');
      setMsgs((p) => [
        ...p,
        {
          role: 'bot',
          type: 'text',
          text: 'Unable to connect to the backend. Please ensure the server is running on localhost:8000.',
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
    // Trigger phase transition animation
    setPhaseTransition(true);
    setTimeout(() => setPhaseTransition(false), 600);
    
    setPhase((i + 1) as Phase);
    setMsgs([]);
    setActs([]);
    setPendingActs([]);
    setCurrentStep(-1);
    setFollowUps([]);
    setTyping(false);
  };

  // Clear chat helper function
  const clearChat = () => {
    setMsgs([]);
    setActs([]);
    setPendingActs([]);
    setCurrentStep(-1);
    setFollowUps([]);
    if (activityTimerRef.current) {
      clearTimeout(activityTimerRef.current);
      activityTimerRef.current = null;
    }
  };

  // Keyboard shortcuts - Escape to clear chat
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && msgs.length > 0) {
        clearChat();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [msgs.length]);

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

    const tid = ensureTraceId();
    const orderQuery = `Order: ${product.name}`;
    const orderHistory: Message[] = [...msgs, { role: 'user', text: orderQuery }];

    // Clear any pending activity timers
    if (activityTimerRef.current) {
      clearTimeout(activityTimerRef.current);
      activityTimerRef.current = null;
    }

    try {
      const response = await processOrder({
        product_id: product.product_id,
        size: product.available_sizes?.[0] || undefined,
        quantity: 1,
        phase,
      });

      // Progressively reveal activities, then show the response
      revealActivitiesProgressively(
        enrichTraceActivities(phase, orderQuery, response.activities, tid, orderHistory, {
          productCount: 0,
        }),
        () => {
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
      return [...prev, { product, quantity: 1, size: product.available_sizes?.[0] }];
    });

    // Show confirmation in chat
    setMsgs((p) => [
      ...p,
      {
        role: 'bot',
        type: 'text',
        text: `Added **${product.name}** to your itinerary! Keep exploring or book when you're ready.`,
      },
    ]);
  };

  // Phase-specific suggestions to demonstrate capabilities and limitations
  const phaseSuggestions: Record<Phase, { works: string[]; breaks: string[]; hint: string }> = {
    1: {
      works: ['City breaks', 'Beach & Resort', 'Business travel under $1500'],
      breaks: ['Romantic week in Europe', 'Family trip with kids who love theme parks'],
      hint: 'Phase 1: keyword lookup only. Try "romantic week in Europe" in Phase 3 to feel the jump →',
    },
    2: {
      works: ['Adventure & Outdoors', 'Wellness & Luxury', 'Tokyo culture trip'],
      breaks: ['Beach vacation with snorkeling', 'Quick conference stopover in Singapore'],
      hint: 'Phase 2: MCP discovers tools — still keywords underneath. Try natural language in Phase 3 →',
    },
    3: {
      works: ['Weekend in Paris under $2k', 'Is the Maldives package available?', 'Family-friendly beach resort'],
      breaks: [],
      hint: 'Phase 3: multi-agent hybrid search. Watch the trace for supervisor + retrieval spans.',
    },
    4: {
      works: [
        'Tokyo trip for two in October',
        'Beach escape under $2500 — remember my food allergies',
        'What did we discuss last time about Iceland?',
      ],
      breaks: [],
      hint: 'Phase 4: same semantic search as Phase 3, plus AgentCore session + Aurora memory in the trace.',
    },
  };

  const currentPhaseSuggestions = phaseSuggestions[phase];

  return (
    <section
      id="agent"
      style={{
        position: 'relative',
        padding: '64px 28px 80px',
        maxWidth: 1180,
        margin: '0 auto',
        borderTop: '1px solid var(--dl-line)',
      }}
    >

        <FadeIn>
          <div style={{ marginBottom: 32 }}>
            <span className="section-label">Live demo</span>
            <h2 className="section-headline">
              Talk to the <em className="serif">agent</em>.
            </h2>
            <p className="section-subtitle">
              Climb the ladder: keywords → MCP → semantic search → memory. Phase 4 is the returning
              traveler — same specialist team, but it remembers you.
            </p>
          </div>
        </FadeIn>

        <div
          className="agent-stage"
          style={{ padding: 20, '--phase-color': pc } as React.CSSProperties}
        >

        {/* Phase pills */}
        <FadeIn delay={0.1}>
          <div style={{ display: 'flex', justifyContent: 'center', gap: 8, marginBottom: 16, flexWrap: 'wrap' }}>
            {phaseLabels.map((label, i) => (
              <button
                key={i}
                onClick={() => switchPhase(i)}
                className={`phase-pill${phase === i + 1 ? ' active' : ''}`}
                style={{
                  '--phase-color': phaseColors[i],
                  transform: phase === i + 1 && phaseTransition ? 'scale(1.05)' : 'scale(1)',
                  boxShadow: phase === i + 1 && phaseTransition ? `0 0 20px ${phaseColors[i]}30` : 'none',
                } as React.CSSProperties}
              >
                {label}
              </button>
            ))}
          </div>

          {/* Phase info panel */}
          <div className="phase-info-bar">
            <div style={{ textAlign: 'center' }}>
              <div className="label">This phase</div>
              <div className="value">{phaseInfo[phase].beat}</div>
            </div>
            <div className="divider" />
            <div>
              <div className="label">Stack</div>
              <div className="value">{phaseInfo[phase].tech}</div>
            </div>
            <div className="divider" />
            <div>
              <div className="label" style={{ color: 'var(--dl-leaf)' }}>✓ Supports</div>
              <div className="value muted">{phaseInfo[phase].capabilities.join(' · ')}</div>
            </div>
            {phaseInfo[phase].limitations.length > 0 && (
              <>
                <div className="divider" />
                <div>
                  <div className="label" style={{ color: 'var(--dl-accent-2)' }}>✗ Limitations</div>
                  <div className="value muted">{phaseInfo[phase].limitations.join(' · ')}</div>
                </div>
              </>
            )}
          </div>
        
        </FadeIn>

        {/* Chat + Activity */}
        <FadeIn delay={0.2}>
          <div className="agent-grid">
            {/* Chat Panel */}
            <div
              className={`chat-panel${phaseTransition ? ' phase-transition' : ''}`}
              style={{ '--phase-color': pc } as React.CSSProperties}
            >
              <div className="chat-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, flex: 1 }}>
                  <div
                    className="status-dot"
                    title={connectionStatus === 'connected' ? 'Backend connected' : connectionStatus === 'checking' ? 'Checking connection...' : 'Backend disconnected'}
                    style={{ 
                      background: connectionStatus === 'connected' ? pc : connectionStatus === 'checking' ? '#f59e0b' : '#ef4444', 
                      boxShadow: `0 0 8px ${connectionStatus === 'connected' ? pc : connectionStatus === 'checking' ? '#f59e0b' : '#ef4444'}` 
                    }}
                  />
                  <span className="chat-title">Travel Concierge</span>
                  {phase === 4 && <MemoryChip compact />}
                  {connectionStatus === 'disconnected' && (
                    <span style={{ 
                      fontSize: 9, 
                      color: '#ef4444', 
                      background: 'rgba(239, 68, 68, 0.1)', 
                      padding: '2px 6px', 
                      borderRadius: 4,
                      fontFamily: 'SF Mono, monospace',
                    }}>
                      Offline
                    </span>
                  )}
                </div>
                {msgs.length > 0 && (
                  <button
                    onClick={clearChat}
                    title="Press Escape to clear"
                    className="chat-clear-btn"
                  >
                    Clear ⎋
                  </button>
                )}
              </div>

              <div className="chat-messages">
                {msgs.length === 0 && !typing && (
                  <div className="chat-empty">
                    <div style={{ fontSize: 36, opacity: 0.3 }}>💬</div>
                    <p style={{ fontSize: 13, color: '#94a3b8', marginBottom: 12 }}>
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
                              className="suggestion-btn warn"
                              style={{ '--phase-color': '#f59e0b' } as React.CSSProperties}
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
                  >
                    {m.role === 'user' ? (
                      m.text
                    ) : m.type === 'products' && m.products ? (
                      <div className="products-response">
                        <p className="products-intro">{m.text}</p>
                        {m.products.map((pr: Product, j: number) => (
                          <div key={j} className="product-result" style={{ position: 'relative' }}>
                            <ProductThumb
                              imageUrl={pr.image_url}
                              category={pr.category}
                              alt={pr.name}
                              style={{
                                width: 48,
                                height: 48,
                                borderRadius: 8,
                                flexShrink: 0,
                              }}
                              emojiSize={22}
                            />
                            <div style={{ flex: 1 }}>
                              <div className="product-result-name">{pr.name}</div>
                              <div className="product-result-meta" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                <span>${pr.price.toFixed(2)} · {pr.brand}</span>
                                <span style={{
                                  fontSize: 9,
                                  fontWeight: 600,
                                  padding: '2px 6px',
                                  borderRadius: 4,
                                  background: 'rgba(16, 185, 129, 0.15)',
                                  color: '#10b981',
                                }}>
                                  ✓ In Stock
                                </span>
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
                                Book Now
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
                            <span style={{ fontWeight: 600, color: pc }}>Booking Confirmed</span>
                          </div>
                          <div style={{ fontSize: 12, color: 'var(--dl-muted)', marginBottom: 8 }}>
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
                            borderTop: '1px solid var(--dl-line)',
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
                              background: 'var(--dl-bg)',
                              border: '1px solid var(--dl-line)',
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
                  style={{ background: 'var(--dl-ink)' }}
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
                  <span className="activity-title">Agent trace</span>
                </div>
                <span className="activity-count" style={{ color: currentStep >= 0 ? pc : undefined, display: 'flex', gap: 6, alignItems: 'center' }}>
                  {traceId && (
                    <button
                      type="button"
                      className="trace-id-pill"
                      title="Permalink preview — full persistence in Wave 02"
                      onClick={() => navigator.clipboard?.writeText(traceId)}
                    >
                      {traceId}
                    </button>
                  )}
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
                    <div style={{ 
                      display: 'flex', 
                      gap: 6, 
                      marginBottom: 12,
                    }}>
                      {[0, 1, 2].map((i) => (
                        <div
                          key={i}
                          style={{
                            width: 8,
                            height: 8,
                            borderRadius: '50%',
                            background: pc,
                            opacity: 0.4,
                            animation: `pulse 1.5s ease-in-out ${i * 0.2}s infinite`,
                          }}
                        />
                      ))}
                    </div>
                    <div style={{ color: '#64748b' }}>Waiting for activity</div>
                    <div style={{ 
                      fontSize: 10, 
                      color: '#475569', 
                      marginTop: 4,
                      fontFamily: 'SF Mono, monospace',
                    }}>
                      Send a query to see the full agent trace
                    </div>
                  </div>
                )}

                {/* Revealed trace spans */}
                {acts.map((a, i) => (
                  <TraceSpan
                    key={a.id || i}
                    entry={a}
                    index={i}
                    isCurrentStep={i === currentStep}
                    phaseColor={pc}
                  />
                ))}

                {/* Pending spans */}
                {pendingActs.map((a, i) => (
                  <TraceSpan
                    key={`pending-${a.id || i}`}
                    entry={a}
                    index={acts.length + i}
                    isCurrentStep={false}
                    isPending
                    phaseColor={pc}
                  />
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
