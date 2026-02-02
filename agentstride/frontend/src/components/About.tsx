/**
 * About Component
 * 
 * Project overview and resources section.
 * Requirements: 6.1, 6.2, 6.3
 */

import { motion } from 'framer-motion'
import { ExternalLink, Github, BookOpen, Users, Sparkles } from 'lucide-react'

export default function About() {
  const resources = [
    {
      title: 'Amazon Bedrock',
      description: 'Foundation models for generative AI applications',
      url: 'https://aws.amazon.com/bedrock/',
      icon: <Sparkles className="w-5 h-5" />,
    },
    {
      title: 'Aurora PostgreSQL',
      description: 'Serverless relational database with pgvector',
      url: 'https://aws.amazon.com/rds/aurora/',
      icon: <BookOpen className="w-5 h-5" />,
    },
    {
      title: 'Strands Agents SDK',
      description: 'Build AI agents with AWS services',
      url: 'https://github.com/strands-agents/sdk-python',
      icon: <Github className="w-5 h-5" />,
    },
    {
      title: 'Model Context Protocol',
      description: 'Standard protocol for AI tool integration',
      url: 'https://modelcontextprotocol.io/',
      icon: <BookOpen className="w-5 h-5" />,
    },
  ]

  const features = [
    'Semantic product search with pgvector',
    'Visual search using Nova 2 Multimodal',
    'Multi-agent orchestration patterns',
    'Real-time activity streaming',
    'Three architectural approaches',
    'Mock mode for offline demos',
  ]

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h1 className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>
          About ClickShop
        </h1>
        <p className="mt-2" style={{ color: 'var(--text-secondary)' }}>
          An AI-powered e-commerce demo showcasing AWS technologies
        </p>
      </motion.div>

      {/* Project Overview - Requirement 6.1 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="card-elevated p-6"
      >
        <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
          Project Overview
        </h2>
        <p className="leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
          ClickShop demonstrates how to build intelligent e-commerce experiences using 
          Amazon Bedrock, Aurora PostgreSQL with pgvector, and the Strands Agents SDK. 
          The demo showcases three architectural patterns for AI agents, from simple 
          direct database access to sophisticated multi-agent systems with visual search.
        </p>
        
        <div className="mt-6 grid grid-cols-2 md:grid-cols-3 gap-3">
          {features.map((feature, index) => (
            <div
              key={index}
              className="flex items-center gap-2 text-sm"
              style={{ color: 'var(--text-secondary)' }}
            >
              <span 
                className="w-1.5 h-1.5 rounded-full flex-shrink-0" 
                style={{ backgroundColor: 'var(--phase-3)' }} 
              />
              {feature}
            </div>
          ))}
        </div>
      </motion.div>

      {/* Resources - Requirement 6.2 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="card-elevated p-6"
      >
        <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
          Resources
        </h2>
        <div className="grid md:grid-cols-2 gap-4">
          {resources.map((resource) => (
            <a
              key={resource.title}
              href={resource.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-start gap-3 p-4 rounded-xl transition-all duration-200 group"
              style={{ 
                backgroundColor: 'var(--bg-tertiary)',
              }}
            >
              <div 
                className="p-2 rounded-lg transition-colors"
                style={{ 
                  backgroundColor: 'var(--bg-secondary)',
                  color: 'var(--text-muted)'
                }}
              >
                {resource.icon}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="font-medium" style={{ color: 'var(--text-primary)' }}>
                    {resource.title}
                  </span>
                  <ExternalLink 
                    className="w-3 h-3 opacity-50 group-hover:opacity-100 transition-opacity" 
                    style={{ color: 'var(--text-muted)' }}
                  />
                </div>
                <p className="text-sm mt-1" style={{ color: 'var(--text-secondary)' }}>
                  {resource.description}
                </p>
              </div>
            </a>
          ))}
        </div>
      </motion.div>

      {/* Credits - Requirement 6.3 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="card-elevated p-6"
      >
        <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
          Credits & Acknowledgments
        </h2>
        <div className="flex items-start gap-4">
          <div 
            className="p-3 rounded-lg"
            style={{ backgroundColor: 'var(--bg-tertiary)' }}
          >
            <Users className="w-6 h-6" style={{ color: 'var(--text-muted)' }} />
          </div>
          <div>
            <p style={{ color: 'var(--text-secondary)' }}>
              Built by the AWS Solutions Architecture team to demonstrate best practices 
              for building AI-powered applications with Amazon Bedrock and Aurora PostgreSQL.
            </p>
            <p className="text-sm mt-3" style={{ color: 'var(--text-muted)' }}>
              This demo is provided as-is for educational purposes. See the LICENSE file 
              for terms of use.
            </p>
          </div>
        </div>
      </motion.div>

      {/* Tech Stack Summary */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <p className="text-center text-sm" style={{ color: 'var(--text-muted)' }}>
          Built with React 18 • Tailwind CSS • Framer Motion • FastAPI • 
          Strands SDK • Amazon Bedrock • Aurora PostgreSQL
        </p>
      </motion.div>
    </div>
  )
}
