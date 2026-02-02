/**
 * OrderConfirmation Component
 * 
 * Displays order details including items, totals, and status.
 * Requirements: 4.6
 */

import { motion } from 'framer-motion'
import { CheckCircle, Package, Truck } from 'lucide-react'
import { Order } from '../types'

interface OrderConfirmationProps {
  order: Order
  phase: 1 | 2 | 3
}

export default function OrderConfirmation({ order, phase }: OrderConfirmationProps) {
  const getPhaseColor = () => {
    switch (phase) {
      case 1: return 'text-blue-400 border-blue-500/30'
      case 2: return 'text-violet-400 border-violet-500/30'
      case 3: return 'text-emerald-400 border-emerald-500/30'
    }
  }

  const getStatusIcon = () => {
    switch (order.status) {
      case 'confirmed':
        return <CheckCircle className="w-5 h-5 text-green-400" />
      case 'processing':
        return <Package className="w-5 h-5 text-amber-400" />
      case 'shipped':
        return <Truck className="w-5 h-5 text-blue-400" />
    }
  }

  const getStatusText = () => {
    switch (order.status) {
      case 'confirmed': return 'Order Confirmed'
      case 'processing': return 'Processing'
      case 'shipped': return 'Shipped'
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`glass-dark rounded-xl border ${getPhaseColor()} overflow-hidden`}
    >
      {/* Header */}
      <div className="p-4 border-b border-white/10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {getStatusIcon()}
            <span className="font-semibold">{getStatusText()}</span>
          </div>
          <span className="text-sm text-gray-400">#{order.order_id}</span>
        </div>
      </div>

      {/* Order Items */}
      <div className="p-4 space-y-3">
        {order.items.map((item, index) => (
          <div key={index} className="flex justify-between items-center">
            <div>
              <span className="text-sm text-white">{item.name}</span>
              {item.size && (
                <span className="text-xs text-gray-400 ml-2">Size: {item.size}</span>
              )}
              <span className="text-xs text-gray-400 ml-2">x{item.quantity}</span>
            </div>
            <span className="text-sm text-gray-300">
              ${(item.unit_price * item.quantity).toFixed(2)}
            </span>
          </div>
        ))}
      </div>

      {/* Totals */}
      <div className="p-4 border-t border-white/10 space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-400">Subtotal</span>
          <span className="text-gray-300">${order.subtotal.toFixed(2)}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-400">Tax</span>
          <span className="text-gray-300">${order.tax.toFixed(2)}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-400">Shipping</span>
          <span className="text-gray-300">${order.shipping.toFixed(2)}</span>
        </div>
        <div className="flex justify-between font-semibold pt-2 border-t border-white/10">
          <span>Total</span>
          <span className={getPhaseColor().split(' ')[0]}>${order.total.toFixed(2)}</span>
        </div>
      </div>

      {/* Estimated Delivery */}
      {order.estimated_delivery && (
        <div className="px-4 pb-4">
          <div className="p-3 rounded-lg bg-white/5 text-center">
            <span className="text-xs text-gray-400">Estimated Delivery</span>
            <p className="text-sm font-medium text-white mt-1">
              {order.estimated_delivery}
            </p>
          </div>
        </div>
      )}
    </motion.div>
  )
}
