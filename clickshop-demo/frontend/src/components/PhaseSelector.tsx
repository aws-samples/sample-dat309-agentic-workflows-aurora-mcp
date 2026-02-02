/**
 * Phase Selector Component
 * 
 * Distinctive phase cards with unique visual identity.
 * Requirements: 4.2, 4.3, 3.5, 3.6, 3.7
 */

import { motion } from 'framer-motion'
import { Database, Zap, ArrowRight, Layers, Network, LucideIcon } from 'lucide-react'

interface PhaseData {
  id: 1 | 2 | 3
  name: string
  description: string
  accentColor: string
  capacity: string
  responseTime: string
}

interface PhaseSelectorProps {
  currentPhase: 1 | 2 | 3
  onPhaseChange: (phase: 1 | 2 | 3) => void
}

const phases: PhaseData[] = [
  {
    id: 1,
    name: 'Direct Access',
    description: 'Single agent talks directly to the database. Fast to build, perfect for prototypes.',
    accentColor: 'var(--phase-1)',
    capacity: 'MVP',
    responseTime: '~2s',
  },
  {
    id: 2,
    name: 'MCP Layer',
    description: 'Agent uses Model Context Protocol for database abstraction. Production-ready pattern.',
    accentColor: 'var(--phase-2)',
    capacity: 'Production',
    responseTime: '~3s',
  },
  {
    id: 3,
    name: 'Multi-Agent',
    description: 'Supervisor orchestrates specialized agents. Semantic search, visual search, and more.',
    accentColor: 'var(--phase-3)',
    capacity: 'Enterprise',
    responseTime: '~200ms',
  },
]

const phaseIcons: Record<1 | 2 | 3, LucideIcon> = {
  1: Database,
  2: Layers,
  3: Network,
}

const phaseEmoji: Record<1 | 2 | 3, string> = {
  1: '🚀',
  2: '🔌',
  3: '🤖',
}

export default function PhaseSelector({ currentPhase, onPhaseChange }: PhaseSelectorProps) {
  return (
    <div className="grid grid-cols-3 gap-4">
      {phases.map((phase) => {
        const Icon = phaseIcons[phase.id]
        const isSelected = currentPhase === phase.id
        
        return (
          <motion.button
            key={phase.id}
            onClick={() => onPhaseChange(phase.id)}
            whileHover={{ y: -4 }}
            whileTap={{ scale: 0.98 }}
            className={`phase-card phase-card-${phase.id} ${isSelected ? 'selected' : ''} text-left`}
          >
            {/* Phase number badge */}
            <div className="flex items-center justify-between mb-4">
              <div 
                className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold"
                style={{ 
                  backgroundColor: isSelected ? phase.accentColor : 'var(--bg-tertiary)',
                  color: isSelected ? 'white' : 'var(--text-secondary)'
                }}
              >
                <span>Phase {phase.id}</span>
                <span>{phaseEmoji[phase.id]}</span>
              </div>
              
              {isSelected && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="flex items-center gap-1 text-xs font-medium"
                  style={{ color: phase.accentColor }}
                >
                  <span>Active</span>
                  <Zap className="w-3.5 h-3.5" />
                </motion.div>
              )}
            </div>

            {/* Icon and title */}
            <div className="flex items-start gap-3 mb-3">
              <div 
                className="p-3 rounded-xl transition-all duration-300"
                style={{ 
                  backgroundColor: isSelected 
                    ? `color-mix(in srgb, ${phase.accentColor} 20%, transparent)` 
                    : 'var(--bg-tertiary)',
                }}
              >
                <Icon 
                  className="w-6 h-6 transition-colors duration-300" 
                  style={{ color: isSelected ? phase.accentColor : 'var(--text-muted)' }}
                />
              </div>
              <div>
                <h3 
                  className="font-bold text-lg transition-colors duration-300"
                  style={{ color: isSelected ? phase.accentColor : 'var(--text-primary)' }}
                >
                  {phase.name}
                </h3>
                <span 
                  className="text-xs font-medium px-2 py-0.5 rounded-full"
                  style={{ 
                    backgroundColor: 'var(--bg-tertiary)',
                    color: 'var(--text-muted)'
                  }}
                >
                  {phase.capacity}
                </span>
              </div>
            </div>

            {/* Description */}
            <p 
              className="text-sm leading-relaxed mb-4"
              style={{ color: 'var(--text-secondary)' }}
            >
              {phase.description}
            </p>

            {/* Stats row */}
            <div 
              className="flex items-center justify-between pt-4 border-t"
              style={{ borderColor: 'var(--border-subtle)' }}
            >
              <div className="flex items-center gap-1.5">
                <Zap className="w-4 h-4" style={{ color: phase.accentColor }} />
                <span className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>
                  {phase.responseTime}
                </span>
              </div>
              
              <motion.div 
                className="flex items-center gap-1 text-sm font-medium"
                style={{ color: isSelected ? phase.accentColor : 'var(--text-muted)' }}
                animate={{ x: isSelected ? 0 : -4, opacity: isSelected ? 1 : 0.5 }}
              >
                <span>Try it</span>
                <ArrowRight className="w-4 h-4" />
              </motion.div>
            </div>
          </motion.button>
        )
      })}
    </div>
  )
}
