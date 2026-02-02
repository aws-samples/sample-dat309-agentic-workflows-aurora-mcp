/**
 * Shop with AI Tab Component
 * 
 * Main shopping interface with chat and activity panel.
 * Requirements: 4.1, 4.2
 */

import { useCallback } from 'react'
import PhaseSelector from './PhaseSelector'
import ChatInterface from './ChatInterface'
import ActivityPanel from './ActivityPanel'
import { useChat } from '../hooks/useChat'
import { useActivity } from '../hooks/useActivity'
import { ActivityEntry } from '../types'

interface ShopWithAIProps {
  currentPhase: 1 | 2 | 3
  onPhaseChange: (phase: 1 | 2 | 3) => void
  isMockMode: boolean
}

export default function ShopWithAI({ 
  currentPhase, 
  onPhaseChange, 
  isMockMode 
}: ShopWithAIProps) {
  const { activities, addActivities } = useActivity({
    enabled: true,
    isMockMode,
  })

  const handleActivity = useCallback((newActivities: ActivityEntry[]) => {
    addActivities(newActivities)
  }, [addActivities])

  const { messages, isLoading, sendMessage, sendImage } = useChat({
    phase: currentPhase,
    isMockMode,
    onActivity: handleActivity,
  })

  return (
    <div className="space-y-6">
      {/* Phase Selector */}
      <PhaseSelector
        currentPhase={currentPhase}
        onPhaseChange={onPhaseChange}
      />

      {/* Split Screen Layout - 58% chat, 42% activity */}
      <div className="flex gap-6 h-[calc(100vh-340px)] min-h-[500px]">
        <div className="w-[58%]">
          <ChatInterface
            phase={currentPhase}
            messages={messages}
            isLoading={isLoading}
            onSendMessage={sendMessage}
            onImageUpload={currentPhase === 3 ? sendImage : undefined}
          />
        </div>

        <div className="w-[42%]">
          <ActivityPanel
            activities={activities}
            phase={currentPhase}
          />
        </div>
      </div>
    </div>
  )
}
