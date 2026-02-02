/**
 * HowItWorks Component
 * 
 * Architecture diagrams and explanations for each phase.
 * Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
 */

import { motion } from 'framer-motion'
import { Database, Server, Cpu, Users, Zap, Shield, ArrowRight } from 'lucide-react'

interface HowItWorksProps {
  currentPhase: 1 | 2 | 3
}

interface TechBadgeProps {
  name: string
  color: string
}

function TechBadge({ name, color }: TechBadgeProps) {
  return (
    <span className={`px-2 py-1 rounded text-xs font-medium ${color}`}>
      {name}
    </span>
  )
}

export default function HowItWorks({ currentPhase }: HowItWorksProps) {
  const phases = [
    {
      id: 1,
      name: 'Phase 1: Direct Database Access',
      description: 'Single agent with direct PostgreSQL connection',
      color: 'blue',
      bgColor: 'bg-blue-500/10',
      borderColor: 'border-blue-500/30',
      textColor: 'text-blue-400',
      architecture: [
        { icon: <Cpu className="w-6 h-6" />, label: 'Strands Agent', sublabel: 'Claude Sonnet 4.5' },
        { icon: <ArrowRight className="w-4 h-4" />, label: '' },
        { icon: <Database className="w-6 h-6" />, label: 'Aurora PostgreSQL', sublabel: 'Direct psycopg3' },
      ],
      techStack: [
        { name: 'Strands SDK', color: 'bg-blue-500/20 text-blue-300' },
        { name: 'Claude Sonnet 4.5', color: 'bg-purple-500/20 text-purple-300' },
        { name: 'psycopg3', color: 'bg-green-500/20 text-green-300' },
        { name: 'pgvector', color: 'bg-cyan-500/20 text-cyan-300' },
      ],
      scaling: 'Best for: Development and small-scale deployments',
      responseTime: '~2-3 seconds',
      codeSnippet: `# Direct database connection
agent = Agent(
    model=BedrockModel("anthropic.claude-sonnet-4-5-20250514-v1:0"),
    tools=[product_lookup, inventory_check, process_order]
)`,
    },
    {
      id: 2,
      name: 'Phase 2: MCP Abstraction',
      description: 'Agent with Model Context Protocol for database access',
      color: 'violet',
      bgColor: 'bg-violet-500/10',
      borderColor: 'border-violet-500/30',
      textColor: 'text-violet-400',
      architecture: [
        { icon: <Cpu className="w-6 h-6" />, label: 'Strands Agent', sublabel: 'Claude Sonnet 4.5' },
        { icon: <ArrowRight className="w-4 h-4" />, label: '' },
        { icon: <Server className="w-6 h-6" />, label: 'MCP Server', sublabel: 'postgres-mcp' },
        { icon: <ArrowRight className="w-4 h-4" />, label: '' },
        { icon: <Database className="w-6 h-6" />, label: 'Aurora PostgreSQL', sublabel: 'RDS Data API' },
      ],
      techStack: [
        { name: 'Strands SDK', color: 'bg-blue-500/20 text-blue-300' },
        { name: 'MCP Protocol', color: 'bg-violet-500/20 text-violet-300' },
        { name: 'RDS Data API', color: 'bg-amber-500/20 text-amber-300' },
        { name: 'pgvector', color: 'bg-cyan-500/20 text-cyan-300' },
      ],
      scaling: 'Best for: Production with connection pooling needs',
      responseTime: '~2-4 seconds',
      codeSnippet: `# MCP-based database access
mcp_client = MCPClient(["awslabs.postgres-mcp-server"])
agent = Agent(
    model=BedrockModel("anthropic.claude-sonnet-4-5-20250514-v1:0"),
    tools=mcp_client.list_tools()  # Auto-discovered
)`,
    },
    {
      id: 3,
      name: 'Phase 3: Multi-Agent System',
      description: 'Supervisor orchestrating specialized agents',
      color: 'emerald',
      bgColor: 'bg-emerald-500/10',
      borderColor: 'border-emerald-500/30',
      textColor: 'text-emerald-400',
      architecture: [
        { icon: <Users className="w-6 h-6" />, label: 'Supervisor', sublabel: 'Orchestrator' },
        { icon: <ArrowRight className="w-4 h-4" />, label: '' },
        { icon: <Cpu className="w-5 h-5" />, label: 'Search Agent', sublabel: 'Nova 2 Multimodal' },
        { icon: <Cpu className="w-5 h-5" />, label: 'Product Agent', sublabel: 'Inventory' },
        { icon: <Cpu className="w-5 h-5" />, label: 'Order Agent', sublabel: 'Processing' },
      ],
      techStack: [
        { name: 'Strands SDK', color: 'bg-blue-500/20 text-blue-300' },
        { name: 'Nova 2 Multimodal', color: 'bg-emerald-500/20 text-emerald-300' },
        { name: 'Multi-Agent', color: 'bg-pink-500/20 text-pink-300' },
        { name: 'Visual Search', color: 'bg-orange-500/20 text-orange-300' },
      ],
      scaling: 'Best for: Complex queries and visual search',
      responseTime: '~3-5 seconds',
      codeSnippet: `# Multi-agent supervisor
supervisor = Agent(
    model=BedrockModel("anthropic.claude-sonnet-4-5-20250514-v1:0"),
    tools=[search_agent.as_tool(), product_agent.as_tool(), 
           order_agent.as_tool()]
)`,
    },
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold">How ClickShop Works</h1>
        <p className="text-gray-400 mt-2">
          Three architectural approaches to AI-powered e-commerce
        </p>
      </div>

      {/* Phase Cards */}
      <div className="space-y-6">
        {phases.map((phase, index) => (
          <motion.div
            key={phase.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`
              glass rounded-xl border ${phase.borderColor}
              ${currentPhase === phase.id ? 'ring-2 ring-offset-2 ring-offset-slate-950' : ''}
              ${currentPhase === phase.id ? `ring-${phase.color}-500` : ''}
            `}
          >
            {/* Phase Header */}
            <div className={`p-6 ${phase.bgColor} border-b border-white/10`}>
              <div className="flex items-center justify-between">
                <div>
                  <h2 className={`text-xl font-semibold ${phase.textColor}`}>
                    {phase.name}
                  </h2>
                  <p className="text-gray-400 mt-1">{phase.description}</p>
                </div>
                <div className="text-right">
                  <div className="flex items-center gap-2 text-sm">
                    <Zap className="w-4 h-4 text-amber-400" />
                    <span className="text-gray-300">{phase.responseTime}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Architecture Diagram */}
            <div className="p-6">
              <h3 className="text-sm font-medium text-gray-400 mb-4">Architecture</h3>
              <div className="flex items-center justify-center gap-4 flex-wrap">
                {phase.architecture.map((item, i) => (
                  <div key={i} className="flex items-center gap-4">
                    {item.label ? (
                      <div className="flex flex-col items-center gap-1">
                        <div className={`p-3 rounded-lg ${phase.bgColor} ${phase.textColor}`}>
                          {item.icon}
                        </div>
                        <span className="text-sm font-medium">{item.label}</span>
                        {item.sublabel && (
                          <span className="text-xs text-gray-500">{item.sublabel}</span>
                        )}
                      </div>
                    ) : (
                      <div className="text-gray-500">{item.icon}</div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Tech Stack */}
            <div className="px-6 pb-4">
              <h3 className="text-sm font-medium text-gray-400 mb-2">Tech Stack</h3>
              <div className="flex flex-wrap gap-2">
                {phase.techStack.map((tech) => (
                  <TechBadge key={tech.name} name={tech.name} color={tech.color} />
                ))}
              </div>
            </div>

            {/* Code Snippet */}
            <div className="px-6 pb-4">
              <h3 className="text-sm font-medium text-gray-400 mb-2">Key Pattern</h3>
              <pre className="p-4 rounded-lg bg-black/30 text-xs text-gray-300 overflow-x-auto">
                <code>{phase.codeSnippet}</code>
              </pre>
            </div>

            {/* Scaling Info */}
            <div className="px-6 pb-6">
              <div className="flex items-center gap-2 text-sm">
                <Shield className="w-4 h-4 text-gray-500" />
                <span className="text-gray-400">{phase.scaling}</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
