/**
 * ProductCard Component
 * 
 * Product display with modern styling.
 * Requirements: 4.5
 */

import { useState } from 'react'
import { motion } from 'framer-motion'
import { ShoppingCart, Package } from 'lucide-react'
import { Product } from '../types'

interface ProductCardProps {
  product: Product
  phase: 1 | 2 | 3
  onAddToCart?: (product: Product, size?: string) => void
}

const phaseColors = {
  1: 'var(--phase-1)',
  2: 'var(--phase-2)',
  3: 'var(--phase-3)',
}

export default function ProductCard({ product, phase, onAddToCart }: ProductCardProps) {
  const [selectedSize, setSelectedSize] = useState<string | undefined>(
    product.available_sizes?.[0]
  )
  const color = phaseColors[phase]

  const getSimilarityBadge = (similarity: number) => {
    if (similarity >= 0.8) return { color: '#10b981', label: 'Great match', emoji: '🎯' }
    if (similarity >= 0.6) return { color: '#f59e0b', label: 'Good match', emoji: '👍' }
    return { color: '#f97316', label: 'Partial match', emoji: '🔍' }
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="rounded-xl overflow-hidden border"
      style={{ 
        backgroundColor: 'var(--bg-secondary)',
        borderColor: 'var(--border-color)'
      }}
    >
      <div className="flex gap-4 p-4">
        {/* Product Image */}
        <div 
          className="w-24 h-24 rounded-xl overflow-hidden flex-shrink-0 flex items-center justify-center"
          style={{ backgroundColor: 'var(--bg-tertiary)' }}
        >
          {product.image_url ? (
            <img
              src={product.image_url}
              alt={product.name}
              className="w-full h-full object-cover"
            />
          ) : (
            <Package className="w-8 h-8" style={{ color: 'var(--text-muted)' }} />
          )}
        </div>

        {/* Product Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div>
              <h3 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>
                {product.name}
              </h3>
              <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>
                {product.brand}
              </p>
            </div>
            
            {/* Similarity Score */}
            {product.similarity !== undefined && (
              <div 
                className="flex items-center gap-1.5 px-2 py-1 rounded-lg"
                style={{ 
                  backgroundColor: `color-mix(in srgb, ${getSimilarityBadge(product.similarity).color} 15%, transparent)`,
                }}
              >
                <span className="text-xs">{getSimilarityBadge(product.similarity).emoji}</span>
                <span 
                  className="text-xs font-semibold"
                  style={{ color: getSimilarityBadge(product.similarity).color }}
                >
                  {(product.similarity * 100).toFixed(0)}%
                </span>
              </div>
            )}
          </div>

          <p 
            className="text-xs mt-2 line-clamp-2 leading-relaxed"
            style={{ color: 'var(--text-secondary)' }}
          >
            {product.description}
          </p>

          <div className="flex items-center justify-between mt-3">
            <span className="text-lg font-bold" style={{ color: 'var(--text-primary)' }}>
              ${product.price.toFixed(2)}
            </span>

            {/* Size Selector */}
            {product.available_sizes && product.available_sizes.length > 0 && (
              <div className="flex gap-1">
                {product.available_sizes.map((size) => (
                  <button
                    key={size}
                    onClick={() => setSelectedSize(size)}
                    className="px-2 py-1 text-[10px] rounded-md font-medium transition-all duration-200"
                    style={{
                      backgroundColor: selectedSize === size 
                        ? `color-mix(in srgb, ${color} 20%, transparent)` 
                        : 'var(--bg-tertiary)',
                      color: selectedSize === size ? color : 'var(--text-muted)'
                    }}
                  >
                    {size}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Add to Cart Button */}
      {onAddToCart && (
        <motion.button
          onClick={() => onAddToCart(product, selectedSize)}
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
          className="w-full py-2.5 flex items-center justify-center gap-2 text-xs font-semibold transition-all duration-200"
          style={{ 
            backgroundColor: color,
            color: 'white'
          }}
        >
          <ShoppingCart className="w-4 h-4" />
          Add to Cart
        </motion.button>
      )}
    </motion.div>
  )
}
