/**
 * Cross-section bridge into the concierge workspace (phase, prompt, send, focus).
 */
import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
  type ReactNode,
} from 'react';
import type { Phase } from '../types';

export interface AgentHandlers {
  phase: Phase;
  setPhase: (phase: Phase) => void;
  setInput: (text: string) => void;
  focusComposer: () => void;
  sendMessage: (text: string) => void;
  clearChat: () => void;
  replayLast: () => void;
}

export interface OpenConciergeOptions {
  phase?: Phase;
  prompt?: string;
  /** When true, submits the prompt immediately (if non-empty). */
  send?: boolean;
  focus?: boolean;
  clear?: boolean;
}

interface AgentBridgeValue {
  register: (handlers: AgentHandlers | null) => void;
  openConcierge: (opts?: OpenConciergeOptions) => void;
  phase: Phase;
}

const AgentBridgeContext = createContext<AgentBridgeValue | null>(null);

export function AgentBridgeProvider({ children }: { children: ReactNode }) {
  const handlersRef = useRef<AgentHandlers | null>(null);
  const phaseRef = useRef<Phase>(4);

  const register = useCallback((handlers: AgentHandlers | null) => {
    handlersRef.current = handlers;
    if (handlers) phaseRef.current = handlers.phase;
  }, []);

  const openConcierge = useCallback((opts?: OpenConciergeOptions) => {
    const h = handlersRef.current;
    if (opts?.clear) h?.clearChat();
    if (opts?.phase != null) {
      h?.setPhase(opts.phase);
      phaseRef.current = opts.phase;
    }
    if (opts?.prompt != null) h?.setInput(opts.prompt);
    if (opts?.send && opts.prompt?.trim()) {
      h?.sendMessage(opts.prompt.trim());
    } else if (opts?.focus !== false) {
      h?.focusComposer();
    }
    document.getElementById('agent')?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  const value = useMemo<AgentBridgeValue>(
    () => ({
      register,
      openConcierge,
      get phase() {
        return phaseRef.current;
      },
    }),
    [register, openConcierge],
  );

  return <AgentBridgeContext.Provider value={value}>{children}</AgentBridgeContext.Provider>;
}

export function useAgentBridge(): AgentBridgeValue {
  const ctx = useContext(AgentBridgeContext);
  if (!ctx) {
    throw new Error('useAgentBridge must be used within AgentBridgeProvider');
  }
  return ctx;
}
