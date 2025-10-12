# ClickShop Agent Evolution Demo

This demo shows the evolution from single agent to multi-agent architecture using the ClickShop use case - a live shopping platform built by two friends using "vibe coding."

## 📖 Story Arc

**The Journey:**
Two friends created ClickShop in a weekend using Claude and "vibe coding." Six months later, they're processing 50K orders/day - still just two friends, still vibe coding. This is their architectural journey.

### Month 1: Single Agent System
- **Scale**: 50 orders/day
- **Architecture**: One agent handles everything
- **Response Time**: ~2 seconds
- **Status**: "Just make it work"

### Month 3: Agent + MCP Tools
- **Scale**: 5,000 orders/day
- **Architecture**: Single agent with specialized MCP tools
- **Response Time**: ~1 second
- **Status**: "Starting to scale"

### Month 6: Multi-Agent Supervisor Pattern
- **Scale**: 50,000 orders/day
- **Architecture**: Supervisor orchestrating specialized agents
- **Response Time**: ~200ms
- **Status**: "Ready for anything"

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- AWS Account with Bedrock access
- Access to Claude Sonnet 4 model in Amazon Bedrock
- AWS CLI configured (optional but recommended)

### Installation

```bash
# 1. Navigate to the demo directory
cd clickshop-demo

# 2. Run the setup script
./setup.sh

# 3. Activate the virtual environment
source venv/bin/activate

# 4. Configure AWS credentials
cp .env.example .env
# Edit .env with your AWS credentials

# 5. Verify setup
python -c "import strands; import boto3; print('✅ Setup successful!')"
```

### Configure AWS Credentials

Edit the `.env` file with your AWS credentials:

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_DEFAULT_REGION=us-west-2

# Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-sonnet-4-20250514-v1:0
BEDROCK_REGION=us-west-2
```

### Verify Bedrock Access

```bash
# Check if you have access to Claude Sonnet 4
aws bedrock list-foundation-models --region us-west-2 | grep claude-sonnet-4
```

---

## 🎬 Running the Demos

### Month 1: Single Agent

**What it demonstrates:**
- Basic agentic loop with ReAct pattern
- Chain of Thought (CoT) reasoning
- Asking clarifying questions
- Sequential tool execution

```bash
python month_1_single_agent.py
```

**Expected output:**
```
🛍️  ClickShop - Month 1: Single Agent Demo
============================================================

📺 Customer watching a live fitness stream...

👤 Customer: I want those running shoes from the stream!

🤖 Agent: I'd be happy to help you order those running shoes! 
What size do you need?

[Demo continues with order processing...]

✅ Demo complete!
💡 What happened:
   1. Agent identified the product from the stream
   2. Agent asked for clarification (size)
   3. Agent checked inventory
   4. Agent calculated total price
   5. Agent processed the order

⏱️  Response time: ~2 seconds
📦 Orders/day capacity: ~50
```

### Month 3: Agent + MCP

**What it demonstrates:**
- Integration with Model Context Protocol
- Specialized tools for different capabilities
- Improved performance with tool specialization
- Still maintainable by two developers

```bash
python month_3_mcp.py
```

### Month 6: Multi-Agent System

**What it demonstrates:**
- Supervisor pattern orchestrating multiple agents
- Parallel processing capabilities
- Specialized agents for different domains
- Production-scale architecture

```bash
python month_6_multi_agent.py
```

---

## 🏗️ Architecture Evolution

### Month 1: Single Agent
```
Customer Request
      ↓
  [Single Agent]
      ↓
  [Tools: Identify, Check, Calculate, Process]
      ↓
   Response
```

**Characteristics:**
- One agent handles all requests
- Sequential processing
- Simple to build and debug
- Perfect for MVP

### Month 3: Agent + MCP
```
Customer Request
      ↓
  [Single Agent]
      ↓
  [MCP Tools]  [Native Tools]
      ↓              ↓
      └──────┬───────┘
           Response
```

**Characteristics:**
- Enhanced with specialized MCP tools
- Tool reusability across projects
- Better separation of concerns
- Faster response times

### Month 6: Multi-Agent Supervisor
```
Customer Request
      ↓
[Supervisor Agent]
      ↓
  ┌───┴───┬───────┬─────────┐
  ↓       ↓       ↓         ↓
[Product][Commerce][Analytics][Notification]
 Agent    Agent    Agent     Agent
  ↓       ↓       ↓         ↓
  └───┬───┴───────┴─────────┘
      ↓
   Response
```

**Characteristics:**
- Parallel processing
- Specialized agents for domains
- Supervisor orchestrates workflow
- Production-scale ready

---

## 🛍️ Use Case: ClickShop

ClickShop is a live shopping platform where:
- 👥 Customers watch influencer live streams
- 🛒 They can instantly purchase products they see
- 🤖 AI agents handle the entire purchase flow
- ⚡ Everything happens in real-time

**The Challenge:**
How do two friends scale from 50 to 50,000 orders/day without hiring a team?

**The Solution:**
Evolve the agent architecture progressively, maintaining "vibe coding" while scaling.

---

## 🔧 Technologies Used

| Technology | Purpose |
|------------|---------|
| **Strands Framework** | Agent orchestration and management |
| **Amazon Bedrock** | Claude Sonnet 4 LLM access |
| **Amazon Aurora** | Serverless PostgreSQL for data persistence |
| **MCP (Model Context Protocol)** | Standardized tool integration |
| **Python** | Primary development language |
| **AWS SDK (boto3)** | AWS service integration |

---

## 📁 Project Structure

```
clickshop-demo/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── .env                         # Your credentials (gitignored)
├── setup.sh                     # Setup script
│
├── month_1_single_agent.py     # Single agent demo
├── month_3_mcp.py              # MCP integration demo
├── month_6_multi_agent.py      # Multi-agent demo
│
├── data/
│   └── products.json           # Mock product data
│
├── demos/
│   └── demo_scenarios.py       # Additional demo scenarios
│
└── .vscode/
    ├── launch.json             # Debug configurations
    └── settings.json           # VSCode settings
```

---

## 🎯 Learning Objectives

By exploring these demos, you'll learn:

1. **Agentic Patterns**
   - ReAct (Reason + Act) loop
   - Chain of Thought reasoning
   - Tool calling and orchestration

2. **Architecture Evolution**
   - When to use single agent vs multi-agent
   - How to scale agent systems
   - Trade-offs between simplicity and capability

3. **Production Practices**
   - Agent observability
   - Error handling
   - Performance optimization
   - Cost management

4. **AWS Integration**
   - Using Amazon Bedrock for LLM access
   - Integrating with Aurora for persistence
   - Building production-ready agent systems

---

## 🐛 Troubleshooting

### Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### AWS Credentials Issues

```bash
# Verify your credentials
aws sts get-caller-identity

# Check Bedrock model access
aws bedrock list-foundation-models --region us-west-2
```

### Bedrock Access Denied

1. Ensure your AWS account has Bedrock enabled
2. Request access to Claude Sonnet 4 in the Bedrock console
3. Verify your IAM permissions include `bedrock:InvokeModel`

### Setup Script Permission Error

```bash
chmod +x setup.sh
```

### Module Not Found Errors

```bash
# Make sure you're in the correct directory
pwd  # Should end with /clickshop-demo

# Verify Python path
which python  # Should point to venv/bin/python
```

---

## 🎓 Demo Tips

### For Presentations

1. **Start with the story** - Two friends, weekend project, explosive growth
2. **Show Month 1 first** - Establish the baseline
3. **Demonstrate the evolution** - Show why each change was necessary
4. **Highlight developer velocity** - Still just two friends maintaining this

### Code Walkthrough Tips

- Focus on the agent definitions and tool implementations
- Show how little code change is needed between iterations
- Emphasize the "vibe coding" philosophy - simple, clear, maintainable

### Live Demo Tips

- Use the mock data for predictable results
- Have backup screenshots in case of connectivity issues
- Show the `.env.example` to explain configuration
- Demonstrate debugging in VSCode if time allows

---

## 📚 Additional Resources

### Strands Framework
- Documentation: https://docs.strands.ai
- GitHub: https://github.com/strands-ai/strands-framework

### Amazon Bedrock
- Documentation: https://docs.aws.amazon.com/bedrock/
- Model Access: https://console.aws.amazon.com/bedrock/

### Model Context Protocol
- Specification: https://modelcontextprotocol.io
- GitHub: https://github.com/modelcontextprotocol

### Agent Patterns
- ReAct Paper: https://arxiv.org/abs/2210.03629
- Chain of Thought: https://arxiv.org/abs/2201.11903

---

## 🤝 Contributing

This is a demo project for educational purposes. If you find issues or have suggestions:

1. Create an issue in the parent repository
2. Submit a pull request with improvements
3. Share your own agent evolution stories!

---

## 📄 License

This demo is part of the AWS samples repository and follows its licensing terms.

---

## 🎉 Next Steps

1. ✅ Run all three demos successfully
2. 📊 Modify the mock data to test different scenarios
3. 🔧 Experiment with different agent prompts
4. 🚀 Try deploying Month 6 architecture to production
5. 📈 Add your own monitoring and observability

---

## 💬 Questions?

- **AWS Support**: https://support.aws.amazon.com
- **Bedrock Documentation**: https://docs.aws.amazon.com/bedrock
- **Repository Issues**: Create an issue in the GitHub repo

---

**Remember:** The goal isn't just to scale - it's to scale while maintaining development velocity and developer happiness. That's the "vibe coding" philosophy! 🚀
