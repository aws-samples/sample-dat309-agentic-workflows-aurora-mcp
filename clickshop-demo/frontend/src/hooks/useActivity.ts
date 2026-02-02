/**
 * useActivity Hook
 * 
 * Manages activity state and WebSocket connection.
 * Requirements: 8.5
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import { ActivityEntry } from '../types'

interface UseActivityOptions {
  enabled: boolean
  isMockMode: boolean
}

interface UseActivityReturn {
  activities: ActivityEntry[]
  isConnected: boolean
  addActivities: (newActivities: ActivityEntry[]) => void
  clearActivities: () => void
}

const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

export function useActivity({ enabled, isMockMode }: UseActivityOptions): UseActivityReturn {
  const [activities, setActivities] = useState<ActivityEntry[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  // Add activities (used by useChat hook for mock mode)
  const addActivities = useCallback((newActivities: ActivityEntry[]) => {
    setActivities(prev => [...prev, ...newActivities])
  }, [])

  // Clear all activities
  const clearActivities = useCallback(() => {
    setActivities([])
  }, [])

  // WebSocket connection for live mode
  useEffect(() => {
    if (!enabled || isMockMode) {
      // Clean up any existing connection
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
      setIsConnected(false)
      return
    }

    const connect = () => {
      try {
        const ws = new WebSocket(`${WS_BASE_URL}/ws/activity`)
        wsRef.current = ws

        ws.onopen = () => {
          setIsConnected(true)
          console.log('Activity WebSocket connected')
        }

        ws.onmessage = (event) => {
          try {
            const activity: ActivityEntry = JSON.parse(event.data)
            setActivities(prev => [...prev, activity])
          } catch (err) {
            console.error('Failed to parse activity:', err)
          }
        }

        ws.onclose = () => {
          setIsConnected(false)
          console.log('Activity WebSocket disconnected')
          
          // Attempt reconnection after 3 seconds
          if (enabled && !isMockMode) {
            reconnectTimeoutRef.current = setTimeout(connect, 3000)
          }
        }

        ws.onerror = (error) => {
          console.error('Activity WebSocket error:', error)
        }
      } catch (err) {
        console.error('Failed to create WebSocket:', err)
        setIsConnected(false)
      }
    }

    connect()

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
    }
  }, [enabled, isMockMode])

  return {
    activities,
    isConnected,
    addActivities,
    clearActivities,
  }
}
