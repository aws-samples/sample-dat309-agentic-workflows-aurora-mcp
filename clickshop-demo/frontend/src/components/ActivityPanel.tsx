/**
 * ActivityPanel Component
 * 
 * Real-time activity feed with personality.
 * Requirements: 4.10, 4.11, 4.12
 */

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown, Search, Package, ShoppingCart, Users, Database, Sparkles, Activity, Zap, Clock } from 'lucide-react'
import { ActivityEntry, ActivityType } from '../types'

interface ActivityPanelProps {
  activities: ActivityEntry[]
  phase: 1 | 2 | 3
}

const activityConfig: Record<ActivityType, { 
  icon: React.ReactNode
  label: string
  color: string
  emoji: string
}> = {
  search: {
    icon: <Search className="w-4 h-4" />,
    label: 'Search',
    color: '#3b82f6',
    emoji: '🔍',
  },
  inventory: {
    icon: <Package className="w-4 h-4" />,
    label: 'Inventory',
    color: '#f59e0b',
    emoji: '📦',
  },
  order: {
    icon: <ShoppingCart className="w-4 h-4" />,
    label: 'Order',
    color: '#10b981',
    emoji: '🛒',
  },
  delegation: {
    icon: <Users className="w-4 h-4" />,
    label: 'Delegation',
    color: '#8b5cf6',
    emoji: '👥',
  },
  mcp: {
    icon: <Database className="w-4 h-4" />,
    label: 'MCP',
    color: '#06b6d4',
    emoji: '🔌',
  },
  embedding: {
    icon: <Sparkles className="w-4 h-4" />,
    label: 'Embedding',
    color: '#ec4899',
    emoji: '✨',
  },
  tool_call: {
    icon: <Zap className="w-4 h-4" />,
    label: 'Tool Call',
    color: '#f97316',
    emoji: '⚡',
  },
  database: {
    icon: <Database className="w-4 h-4" />,
    label: 'Database',
    color: '#14b8a6',
    emoji: '💾',
  },
  error: {
    icon: <Activity className="w-4 h-4" />,
    label: 'Error',
    color: '#ef4444',
    emoji: '❌',
  },
}

const phaseConfig = {
  1: { color: 'var(--phase-1)', emoji: '🚀' },
  2: { color: 'var(--phase-2)', emoji: '🔌' },
  3: { color: 'var(--phase-3)', emoji: '🤖' },
}

function ActivityItem({ activity, index }: { activity: ActivityEntry; index: number }) {
  const [isExpanded, setIsExpanded] = useState(false)
  const config = activityConfig[activity.activity_type] || activityConfig.search

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
      className="rounded-xl overflow-hidden"
      style={{ backgroundColor: 'var(--bg-tertiary)' }}
    >
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-3.5 flex items-start gap-3 text-left transition-colors hover:opacity-90"
      >
        <div 
          className="p-2 rounded-lg flex-shrink-0"
          style={{ backgroundColor: `color-mix(in srgb, ${config.color} 15%, transparent)` }}
        >
          <span style={{ color: config.color }}>{config.icon}</span>
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-medium text-sm" style={{ color: 'var(--text-primary)' }}>
              {activity.title}
            </span>
            <span className="text-xs">{config.emoji}</span>
            {activity.agent_name && (
              <span 
                className="text-[10px] px-2 py-0.5 rounded-full font-medium"
                style={{ 
                  backgroundColor: 'var(--bg-secondary)',
                  color: 'var(--text-muted)'
                }}
              >
                {activity.agent_name}
              </span>
            )}
          </div>
          
          <div className="flex items-center gap-3 mt-1.5">
            <div className="flex items-center gap-1">
              <Clock className="w-3 h-3" style={{ color: 'var(--text-muted)' }} />
              <span className="text-[11px]" style={{ color: 'var(--text-muted)' }}>
                {new Date(activity.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
              </span>
            </div>
            {activity.execution_time_ms !== undefined && (
              <div className="flex items-center gap-1">
                <Zap className="w-3 h-3" style={{ color: config.color }} />
                <span 
                  className="text-[10px] font-mono font-medium"
                  style={{ color: config.color }}
                >
                  {activity.execution_time_ms}ms
                </span>
              </div>
            )}
          </div>
        </div>

        {(activity.details || activity.sql_query) && (
          <motion.div
            animate={{ rotate: isExpanded ? 180 : 0 }}
            transition={{ duration: 0.2 }}
            style={{ color: 'var(--text-muted)' }}
          >
            <ChevronDown className="w-4 h-4" />
          </motion.div>
        )}
      </button>

      <AnimatePresence>
        {isExpanded && (activity.details || activity.sql_query) && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-3.5 pb-3.5 space-y-2.5">
              {activity.details && (
                <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
                  {activity.details}
                </p>
              )}
              
              {activity.sql_query && (
                <div 
                  className="p-3 rounded-lg border"
                  style={{ 
                    backgroundColor: 'var(--bg-secondary)',
                    borderColor: 'var(--border-subtle)'
                  }}
                >
                  <pre 
                    className="font-mono text-[11px] overflow-x-auto whitespace-pre-wrap leading-relaxed"
                    style={{ color: 'var(--text-secondary)' }}
                  >
                    {activity.sql_query}
                  </pre>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

export default function ActivityPanel({ activities, phase }: ActivityPanelProps) {
  const config = phaseConfig[phase]

  return (
    <div className="h-full flex flex-col card-elevated overflow-hidden">
      {/* Header */}
      <div 
        className="px-5 py-4 border-b"
        style={{ borderColor: 'var(--border-color)' }}
      >
        <div className="flex items-center gap-3">
          <div 
            className="p-2.5 rounded-xl"
            style={{ backgroundColor: `color-mix(in srgb, ${config.color} 15%, transparent)` }}
          >
            <Activity className="w-5 h-5" style={{ color: config.color }} />
          </div>
          <div>
            <h2 className="font-semibold" style={{ color: 'var(--text-primary)' }}>
              Agent Activity
            </h2>
            <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
              Real-time operations {config.emoji}
            </span>
          </div>
        </div>
      </div>

      {/* Activity List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2.5 custom-scroll">
        {activities.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center px-6">
            {/* Animated empty state */}
            <div className="relative mb-4">
              <motion.div
                className="w-16 h-16 rounded-2xl flex items-center justify-center"
                style={{ backgroundColor: 'var(--bg-tertiary)' }}
                animate={{ scale: [1, 1.05, 1] }}
                transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
              >
                <Activity className="w-8 h-8" style={{ color: 'var(--text-muted)' }} />
              </motion.div>
              
              {/* Orbiting dots */}
              {[0, 1, 2].map((i) => (
                <motion.div
                  key={i}
                  className="absolute w-2 h-2 rounded-full"
                  style={{ 
                    backgroundColor: config.color,
                    top: '50%',
                    left: '50%',
                  }}
                  animate={{
                    x: [0, 30 * Math.cos((i * 2 * Math.PI) / 3), 0],
                    y: [0, 30 * Math.sin((i * 2 * Math.PI) / 3), 0],
                    opacity: [0.3, 1, 0.3],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    delay: i * 0.3,
                    ease: 'easeInOut',
                  }}
                />
              ))}
            </div>

            <h3 className="font-semibold mb-1" style={{ color: 'var(--text-primary)' }}>
              Waiting for action
            </h3>
            <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
              Activity will appear here as the AI processes your requests
            </p>
          </div>
        ) : (
          <AnimatePresence initial={false}>
            {activities.map((activity, index) => (
              <ActivityItem key={activity.id} activity={activity} index={index} />
            ))}
          </AnimatePresence>
        )}
      </div>
    </div>
  )
}
