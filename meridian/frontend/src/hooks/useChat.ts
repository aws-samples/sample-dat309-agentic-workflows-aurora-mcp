/**
 * useChat Hook
 * 
 * Manages chat state and API communication.
 * Requirements: 4.9, 8.2, 8.3
 */

import { useState, useCallback } from 'react'
import { Message, ChatResponse, Product, Order, ActivityEntry } from '../types'
import { generateMockResponse, getPhaseDelay } from '../mock/mockData'

// Extended message type for internal use with id and timestamp
interface ChatMessage extends Message {
  id: string;
  timestamp: Date;
  content: string;
  orderConfirmation?: Order;
}

interface UseChatOptions {
  phase: 1 | 2 | 3
  isMockMode: boolean
  onActivity?: (activities: ActivityEntry[]) => void
}

interface UseChatReturn {
  messages: ChatMessage[]
  isLoading: boolean
  error: string | null
  sendMessage: (message: string) => Promise<void>
  sendImage: (file: File) => Promise<void>
  clearMessages: () => void
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export function useChat({ phase, isMockMode, onActivity }: UseChatOptions): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const addMessage = useCallback((
    role: 'user' | 'bot',
    content: string,
    products?: Product[],
    orderConfirmation?: Order
  ) => {
    const message: ChatMessage = {
      id: crypto.randomUUID(),
      role,
      text: content,
      content,
      timestamp: new Date(),
      products,
      orderConfirmation,
    }
    setMessages((prev: ChatMessage[]) => [...prev, message])
    return message
  }, [])

  const sendMessage = useCallback(async (message: string) => {
    if (!message.trim()) return

    setError(null)
    addMessage('user', message)
    setIsLoading(true)

    try {
      if (isMockMode) {
        // Mock mode - simulate delay and generate response
        const delay = getPhaseDelay(phase)
        await new Promise(resolve => setTimeout(resolve, delay))
        
        const response = generateMockResponse(message, phase)
        addMessage('bot', response.message, response.products, response.order)
        
        if (onActivity && response.activities) {
          onActivity(response.activities)
        }
      } else {
        // Live mode - call API
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message,
            phase,
            conversation_id: crypto.randomUUID(),
          }),
        })

        if (!response.ok) {
          throw new Error(`API error: ${response.status}`)
        }

        const data: ChatResponse = await response.json()
        addMessage('bot', data.message, data.products, data.order)
        
        if (onActivity && data.activities) {
          onActivity(data.activities)
        }
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMessage)
      addMessage('bot', `Sorry, I encountered an error: ${errorMessage}. Please try again.`)
    } finally {
      setIsLoading(false)
    }
  }, [phase, isMockMode, addMessage, onActivity])

  const sendImage = useCallback(async (file: File) => {
    if (phase !== 3) {
      setError('Image search is only available in Phase 3')
      return
    }

    setError(null)
    addMessage('user', `[Image uploaded: ${file.name}]`)
    setIsLoading(true)

    try {
      if (isMockMode) {
        // Mock mode - simulate visual search
        const delay = getPhaseDelay(phase)
        await new Promise(resolve => setTimeout(resolve, delay))
        
        const response = generateMockResponse('visual search for uploaded image', phase)
        addMessage('bot', 'Based on your image, here are similar products:', response.products)
        
        if (onActivity && response.activities) {
          onActivity(response.activities)
        }
      } else {
        // Live mode - upload image
        const formData = new FormData()
        formData.append('image', file)
        formData.append('phase', String(phase))

        const response = await fetch(`${API_BASE_URL}/api/chat/image`, {
          method: 'POST',
          body: formData,
        })

        if (!response.ok) {
          throw new Error(`API error: ${response.status}`)
        }

        const data: ChatResponse = await response.json()
        addMessage('bot', data.message, data.products, data.order)
        
        if (onActivity && data.activities) {
          onActivity(data.activities)
        }
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMessage)
      addMessage('bot', `Sorry, I couldn't process your image: ${errorMessage}`)
    } finally {
      setIsLoading(false)
    }
  }, [phase, isMockMode, addMessage, onActivity])

  const clearMessages = useCallback(() => {
    setMessages([])
    setError(null)
  }, [])

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    sendImage,
    clearMessages,
  }
}

export type { ChatMessage }
