/**
 * ChatInterface Component
 * 
 * Modern chat interface with personality and empty states.
 * Requirements: 4.1, 4.4, 4.7, 4.8
 */

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Image, MessageCircle, Sparkles, ShoppingBag, Search, Package } from 'lucide-react'
import { ChatMessage } from '../hooks/useChat'
import ProductCard from './ProductCard'
import OrderConfirmation from './OrderConfirmation'

interface ChatInterfaceProps {
  phase: 1 | 2 | 3
  messages: ChatMessage[]
  isLoading: boolean
  onSendMessage: (message: string) => void
  onImageUpload?: (file: File) => void
}

const phaseConfig = {
  1: { color: 'var(--phase-1)', name: 'Direct', emoji: '🚀' },
  2: { color: 'var(--phase-2)', name: 'MCP', emoji: '🔌' },
  3: { color: 'var(--phase-3)', name: 'Multi-Agent', emoji: '🤖' },
}

const suggestions = [
  { icon: Search, text: 'Running shoes under $150' },
  { icon: Package, text: 'Nike' },
  { icon: ShoppingBag, text: 'Fitness equipment' },
]

export default function ChatInterface({
  phase,
  messages,
  isLoading,
  onSendMessage,
  onImageUpload,
}: ChatInterfaceProps) {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const config = phaseConfig[phase]

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim())
      setInput('')
    }
  }

  const handleSuggestionClick = (text: string) => {
    if (!isLoading) {
      onSendMessage(text)
    }
  }

  return (
    <div 
      className="h-full flex flex-col card-elevated overflow-hidden"
    >
      {/* Header */}
      <div 
        className="px-5 py-4 border-b flex items-center justify-between"
        style={{ borderColor: 'var(--border-color)' }}
      >
        <div className="flex items-center gap-3">
          <div 
            className="p-2.5 rounded-xl"
            style={{ backgroundColor: `color-mix(in srgb, ${config.color} 15%, transparent)` }}
          >
            <MessageCircle className="w-5 h-5" style={{ color: config.color }} />
          </div>
          <div>
            <h2 className="font-semibold" style={{ color: 'var(--text-primary)' }}>
              AI Shopping Assistant
            </h2>
            <div className="flex items-center gap-2">
              <span 
                className="w-2 h-2 rounded-full animate-pulse"
                style={{ backgroundColor: config.color }}
              />
              <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
                {config.name} Mode {config.emoji}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-5 custom-scroll">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center px-8">
            {/* Animated illustration */}
            <div className="relative mb-6">
              <motion.div
                className="w-20 h-20 rounded-2xl flex items-center justify-center"
                style={{ backgroundColor: `color-mix(in srgb, ${config.color} 10%, transparent)` }}
                animate={{ y: [0, -8, 0] }}
                transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
              >
                <ShoppingBag className="w-10 h-10" style={{ color: config.color }} />
              </motion.div>
              <motion.div
                className="absolute -right-2 -top-2 w-8 h-8 rounded-lg flex items-center justify-center"
                style={{ backgroundColor: 'var(--bg-secondary)', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}
                animate={{ rotate: [0, 10, -10, 0], scale: [1, 1.1, 1] }}
                transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
              >
                <Sparkles className="w-4 h-4 text-amber-500" />
              </motion.div>
            </div>

            <h3 className="text-xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>
              Ready to help you shop! {config.emoji}
            </h3>
            <p className="text-sm mb-6 max-w-sm" style={{ color: 'var(--text-secondary)' }}>
              Ask me about products, check inventory, or place an order. 
              {phase === 3 && ' You can even upload an image to find similar items!'}
            </p>

            {/* Suggestion chips */}
            <div className="flex flex-col gap-2 w-full max-w-sm">
              <span className="text-xs font-medium" style={{ color: 'var(--text-muted)' }}>
                Try asking:
              </span>
              {suggestions.map((suggestion, i) => (
                <motion.button
                  key={i}
                  onClick={() => handleSuggestionClick(suggestion.text)}
                  whileHover={{ scale: 1.02, x: 4 }}
                  whileTap={{ scale: 0.98 }}
                  className="flex items-center gap-3 p-3 rounded-xl text-left transition-colors"
                  style={{ 
                    backgroundColor: 'var(--bg-tertiary)',
                    color: 'var(--text-secondary)'
                  }}
                >
                  <suggestion.icon className="w-4 h-4" style={{ color: config.color }} />
                  <span className="text-sm">{suggestion.text}</span>
                </motion.button>
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <AnimatePresence initial={false}>
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 10, scale: 0.98 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.98 }}
                  transition={{ duration: 0.2 }}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className="max-w-[85%] rounded-2xl px-4 py-3"
                    style={{
                      backgroundColor: message.role === 'user' ? config.color : 'var(--bg-tertiary)',
                      color: message.role === 'user' ? 'white' : 'var(--text-primary)'
                    }}
                  >
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
                    
                    {message.products && message.products.length > 0 && (
                      <div className="mt-4 grid gap-3">
                        {message.products.map((product) => (
                          <ProductCard key={product.product_id} product={product} phase={phase} />
                        ))}
                      </div>
                    )}

                    {message.orderConfirmation && (
                      <div className="mt-4">
                        <OrderConfirmation order={message.orderConfirmation} phase={phase} />
                      </div>
                    )}

                    <span 
                      className="text-[10px] mt-2 block"
                      style={{ opacity: 0.6 }}
                    >
                      {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>

            {/* Typing Indicator */}
            <AnimatePresence>
              {isLoading && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="flex justify-start"
                >
                  <div 
                    className="rounded-2xl px-4 py-3 flex items-center gap-3"
                    style={{ backgroundColor: 'var(--bg-tertiary)' }}
                  >
                    <div className="flex gap-1">
                      {[0, 1, 2].map((i) => (
                        <motion.div
                          key={i}
                          className="w-2 h-2 rounded-full"
                          style={{ backgroundColor: config.color }}
                          animate={{ y: [0, -6, 0] }}
                          transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.15 }}
                        />
                      ))}
                    </div>
                    <span className="text-sm" style={{ color: 'var(--text-muted)' }}>
                      Thinking...
                    </span>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <form 
        onSubmit={handleSubmit} 
        className="p-4 border-t"
        style={{ borderColor: 'var(--border-color)' }}
      >
        <div className="flex gap-3">
          {phase === 3 && onImageUpload && (
            <>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={(e) => {
                  const file = e.target.files?.[0]
                  if (file) onImageUpload(file)
                  if (fileInputRef.current) fileInputRef.current.value = ''
                }}
                className="hidden"
              />
              <motion.button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="p-3 rounded-xl transition-colors"
                style={{ backgroundColor: 'var(--bg-tertiary)' }}
                title="Upload image for visual search"
              >
                <Image className="w-5 h-5" style={{ color: config.color }} />
              </motion.button>
            </>
          )}

          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSubmit(e)
              }
            }}
            placeholder="Ask about products, inventory, or orders..."
            disabled={isLoading}
            className="input-field flex-1"
            style={{
              ['--phase-color' as string]: config.color,
            }}
          />

          <motion.button
            type="submit"
            disabled={!input.trim() || isLoading}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="p-3 rounded-xl transition-all disabled:opacity-40 disabled:cursor-not-allowed"
            style={{ 
              backgroundColor: config.color,
              color: 'white'
            }}
          >
            <Send className="w-5 h-5" />
          </motion.button>
        </div>
      </form>
    </div>
  )
}
