/**
 * HowItWorks Component
 * 
 * Architecture diagrams and explanations for each phase.
 * Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
 */

import { motion } from 'framer-motion'
import { Database, Cpu, Users, ArrowRight, Layers, Network, CheckCircle2 } from 'lucide-react'

interface HowItWorksProps {
  currentPhase: 1 | 2 | 3
}

const phases = [
  {
    id: 1,
    name: 'Phase 1: Direct Access',
    tagline: 'Simple & Fast',
    emoji: '🚀',
    description: 'Agent connects directly to Aurora PostgreSQL. Perfect for MVPs and prototypes.',
    color: 'var(--phase-1)',
    architecture: [
      { icon: Cpu, label: 'Strands Agent', sublabel: 'Claude Sonnet' },
      { icon: Database, label: 'Aurora PostgreSQL', sublabel: 'RDS Data API' },
    ],
    techStack: ['Strands SDK', 'Claude Sonnet', 'RDS Data API', 'Aurora PostgreSQL'],
    pros: ['Fastest to implement', 'Lowest latency', 'Simple debugging'],
    codeSnippet: `agent = Agent(
    model=BedrockModel("claude-sonnet"),
    tools=[product_lookup, inventory_check]
)`,
  },
  {
    id: 2,
    name: 'Phase 2: MCP Layer',
    tagline: 'Production Ready',
    emoji: '🔌',
    description: 'Agent uses Model Context Protocol for database abstraction. Portable and scalable.',
    color: 'var(--phase-2)',
    architecture: [
      { icon: Cpu, label: 'Strands Agent', sublabel: 'Claude Sonnet' },
      { icon: Layers, label: 'MCP Server', sublabel: 'postgres-mcp' },
      { icon: Database, label: 'Aurora PostgreSQL', sublabel: 'RDS Data API' },
    ],
    techStack: ['Strands SDK', 'MCP Protocol', 'RDS Data API', 'pgvector'],
    pros: ['Database portability', 'Connection pooling', 'Tool auto-discovery'],
    codeSnippet: `mcp = MCPClient(["postgres-mcp-server"])
agent = Agent(
    model=BedrockModel("claude-sonnet"),
    tools=mcp.list_tools()  # Auto-discovered
)`,
  },
  {
    id: 3,
    name: 'Phase 3: Multi-Agent',
    tagline: 'Enterprise Grade',
    emoji: '🤖',
    description: 'Supervisor orchestrates specialized agents. Semantic search, visual search, and more.',
    color: 'var(--phase-3)',
    architecture: [
      { icon: Users, label: 'Supervisor', sublabel: 'Orchestrator' },
      { icon: Network, label: 'Search Agent', sublabel: 'Nova Embeddings' },
      { icon: Cpu, label: 'Product Agent', sublabel: 'Inventory' },
      { icon: Cpu, label: 'Order Agent', sublabel: 'Processing' },
    ],
    techStack: ['Strands SDK', 'Multi-Agent', 'Nova Embeddings', 'Visual Search'],
    pros: ['Specialized agents', 'Semantic search', 'Visual search', 'Parallel processing'],
    codeSnippet: `supervisor = Agent(
    model=BedrockModel("claude-sonnet"),
    tools=[
        search_agent.as_tool(),
        product_agent.as_tool(),
        order_agent.as_tool()
    ]
)`,
  },
]

export default function HowItWorks({ currentPhase }: HowItWorksProps) {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>
          How ClickShop Works
        </h1>
        <p className="mt-2" style={{ color: 'var(--text-secondary)' }}>
          Three architectural approaches to AI-powered e-commerce
        </p>
      </div>

      {/* Phase Cards */}
      <div className="space-y-6">
        {phases.map((phase, index) => {
          const isActive = currentPhase === phase.id
          return (
            <motion.div
              key={phase.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <div 
                className="card-elevated overflow-hidden"
                style={{
                  borderColor: isActive ? phase.color : 'var(--border-color)',
                  borderWidth: isActive ? '2px' : '1px',
                  borderStyle: 'solid',
                }}
              >
              {/* Header */}
              <div 
                className="p-6 border-b"
                style={{ 
                  borderColor: 'var(--border-color)',
                  background: isActive 
                    ? `linear-gradient(135deg, color-mix(in srgb, ${phase.color} 10%, transparent), transparent)`
                    : undefined
                }}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <span className="text-3xl">{phase.emoji}</span>
                    <div>
                      <div className="flex items-center gap-2">
                        <h2 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>
                          {phase.name}
                        </h2>
                        {isActive && (
                          <span 
                            className="px-2 py-0.5 rounded-full text-xs font-medium"
                            style={{ backgroundColor: phase.color, color: 'white' }}
                          >
                            Active
                          </span>
                        )}
                      </div>
                      <p style={{ color: 'var(--text-secondary)' }}>{phase.description}</p>
                    </div>
                  </div>
                  <div 
                    className="px-3 py-1.5 rounded-full text-sm font-medium"
                    style={{ 
                      backgroundColor: `color-mix(in srgb, ${phase.color} 15%, transparent)`,
                      color: phase.color
                    }}
                  >
                    {phase.tagline}
                  </div>
                </div>
              </div>

              {/* Architecture */}
              <div className="p-6">
                <h3 className="text-sm font-semibold mb-4" style={{ color: 'var(--text-muted)' }}>
                  ARCHITECTURE
                </h3>
                <div className="flex items-center justify-center gap-4 flex-wrap">
                  {phase.architecture.map((item, i) => (
                    <div key={i} className="flex items-center gap-4">
                      <div className="flex flex-col items-center gap-2">
                        <div 
                          className="p-4 rounded-xl"
                          style={{ 
                            backgroundColor: `color-mix(in srgb, ${phase.color} 10%, transparent)`,
                          }}
                        >
                          <item.icon className="w-6 h-6" style={{ color: phase.color }} />
                        </div>
                        <div className="text-center">
                          <div className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                            {item.label}
                          </div>
                          <div className="text-xs" style={{ color: 'var(--text-muted)' }}>
                            {item.sublabel}
                          </div>
                        </div>
                      </div>
                      {i < phase.architecture.length - 1 && (
                        <ArrowRight className="w-5 h-5" style={{ color: 'var(--text-muted)' }} />
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Tech Stack & Pros */}
              <div className="grid md:grid-cols-2 gap-6 p-6 border-t" style={{ borderColor: 'var(--border-color)' }}>
                {/* Tech Stack */}
                <div>
                  <h3 className="text-sm font-semibold mb-3" style={{ color: 'var(--text-muted)' }}>
                    TECH STACK
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {phase.techStack.map((tech) => (
                      <span 
                        key={tech}
                        className="px-3 py-1.5 rounded-lg text-xs font-medium"
                        style={{ 
                          backgroundColor: 'var(--bg-tertiary)',
                          color: 'var(--text-secondary)'
                        }}
                      >
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Pros */}
                <div>
                  <h3 className="text-sm font-semibold mb-3" style={{ color: 'var(--text-muted)' }}>
                    BENEFITS
                  </h3>
                  <div className="space-y-2">
                    {phase.pros.map((pro) => (
                      <div key={pro} className="flex items-center gap-2">
                        <CheckCircle2 className="w-4 h-4" style={{ color: '#10b981' }} />
                        <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>{pro}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Code Snippet */}
              <div className="p-6 border-t" style={{ borderColor: 'var(--border-color)' }}>
                <h3 className="text-sm font-semibold mb-3" style={{ color: 'var(--text-muted)' }}>
                  KEY PATTERN
                </h3>
                <pre 
                  className="p-4 rounded-xl text-xs overflow-x-auto"
                  style={{ 
                    backgroundColor: 'var(--bg-tertiary)',
                    color: 'var(--text-secondary)'
                  }}
                >
                  <code>{phase.codeSnippet}</code>
                </pre>
              </div>
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
