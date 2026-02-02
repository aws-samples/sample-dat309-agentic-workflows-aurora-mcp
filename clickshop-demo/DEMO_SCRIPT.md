# AgentStride Demo Script

## Building Agentic e-Commerce Applications with Aurora PostgreSQL and MCP

**Duration:** 60 minutes  
**Format:** Live coding walkthrough with webapp demonstration

---

## Key Files Reference

Before we begin, here are the important files you may want to show during the demo:

| File                                        | Purpose                    | Key Lines                                            |
| ------------------------------------------- | -------------------------- | ---------------------------------------------------- |
| `backend/routers/chat.py`                   | Main API with all 3 phases | Phase 1: 272-305, Phase 2: 339-395, Phase 3: 407-560 |
| `backend/db/rds_data_client.py`             | Direct database connection | Class: 16-170, execute(): 134-167                    |
| `backend/mcp/mcp_client.py`                 | MCP protocol client        | connect_to_database(): 159-193, run_query(): 195-220 |
| `backend/db/embedding_service.py`           | Nova embeddings            | generate_text_embedding(): 54-90                     |
| `backend/search_utils.py`                   | Search query parsing       | parse_search_query(): 24-58                          |
| `frontend/src/components/PhaseSelector.tsx` | Phase selection UI         | -                                                    |
| `frontend/src/components/ActivityPanel.tsx` | Shows agent activities     | -                                                    |
| `frontend/src/components/ChatInterface.tsx` | Chat UI component          | -                                                    |

---

## Pre-Demo Setup (Do this 5 minutes before)

Open two terminal windows:

**Terminal 1 - Backend:**

```bash
cd clickshop-demo
source venv/bin/activate
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**

```bash
cd clickshop-demo/frontend
npm run dev
```

**Verify everything works:**

- Open http://localhost:5173 in your browser
- You should see the AgentStride homepage
- Try a quick search to make sure the backend responds

---

## Part 1: Introduction (5 minutes)

### What to Say:

> "Welcome everyone. Today I'm going to show you how to build agentic applications using Aurora PostgreSQL. We're going to look at a demo called AgentStride, which is an agentic shopping assistant."

> "What makes this interesting is that we're going to see three different architectural patterns for connecting AI agents to your database. Each pattern represents a real evolution that teams go through as they build and scale agentic AI applications."

> "Let me show you the three phases we'll cover:"

**Point to the Phase Selector in the UI and explain:**

> "Phase 1 is the simplest approach. We connect directly to Aurora using the RDS Data API. The AI agent takes your question, figures out what SQL to run, and gets the results. It's straightforward and great for getting started."

> "Phase 2 introduces something called MCP, which stands for Model Context Protocol. This is an open standard that provides a clean abstraction layer between your AI agent and the database. Same functionality, but now it's standardized and portable."

> "Phase 3 is where things get really interesting. We add semantic search using pgvector. This means the AI doesn't just match keywords anymore. It actually understands what you mean. If you ask for 'comfortable shoes for long runs', it knows you want cushioned running shoes, even if those exact words aren't in the product description."

---

## Part 2: Phase 1 - Direct Database Connection (15 minutes)

### What to Say:

> "Let's start with Phase 1. This is the foundation that everything else builds on."

**Click on Phase 1 in the UI**

> "When you select Phase 1, the application connects directly to Aurora PostgreSQL using the RDS Data API. This is a serverless-friendly way to talk to your database. You don't need to manage connection pools or worry about connections timing out."

### Demo Query 1: Basic Category Search

**Type in the chat:** `running shoes`

> "Let me search for running shoes. Watch the Activity Panel on the right side of the screen."

**Point to the Activity Panel and explain each step:**

> "You can see exactly what's happening behind the scenes:"
>
> - "First, it says 'Processing with Direct RDS Data API' - that tells us we're in Phase 1"
> - "Then 'Direct RDS Data API connection' - the agent is connecting to Aurora"
> - "Next, 'Category filter: Running Shoes' - the agent figured out this is a category search"
> - "Finally, 'Found 4 products' - we got our results"

> "The agent translated my natural language query into a SQL query that filters by the Running Shoes category."

### Code Walkthrough (Optional - if audience is technical):

**Open `backend/routers/chat.py` and scroll to line 272:**

> "Let me show you the code. This is the phase1_search function starting at line 272."

> "You can see it's pretty simple:"
>
> - "We get a database client using get_rds_data_client()"
> - "We parse the search query to understand what the user wants"
> - "We execute a keyword search against the database"
> - "We return the products"

### Demo Query 2: Brand Search

**Type in the chat:** `Nike shoes`

> "Now let me search for a specific brand. I'll type 'Nike shoes'."

> "Notice the activity says 'Searching shoe categories'. The agent recognized Nike as a brand and searched across all shoe categories for Nike products."

### Demo Query 3: Price Filter

**Type in the chat:** `shoes under $150`

> "The agent also understands price constraints. Let me search for 'shoes under $150'."

> "You can see it found products that match both the category and the price filter. This is all done through SQL WHERE clauses."

### Demo Query 4: Different Category

**Type in the chat:** `fitness equipment`

> "Let's try a completely different category. I'll search for 'fitness equipment'."

> "Same pattern, different category. The agent maps my query to the Fitness Equipment category and returns relevant products."

### Showing the Limitation

**Type in the chat:** `gear for my first marathon`

> "Now here's where Phase 1 shows its limitation. Let me search for 'gear for my first marathon'."

> "Look at the results - we got nothing back. Zero products. That's because Phase 1 only does keyword matching. It doesn't understand what 'marathon' means or what gear a first-time marathoner would need."

**Now try:** `breathable clothes for hot weather`

> "But watch this - if I search for 'breathable clothes for hot weather', I get results. Why? Because the word 'clothes' happens to match our Apparel category."

> "This is the inconsistency of keyword search. Sometimes it works by accident because you happened to use the right word. Sometimes it fails completely. Users have no way to predict what will work."

> "The user asking about marathon gear and the user asking about breathable clothes have the same intent - they want relevant products. But one gets results and one doesn't, purely based on keyword luck."

> "This is where Phase 3 will really shine. But first, let's look at Phase 2."

### Real-World Pros and Cons of Phase 1

**When to use this approach (The Story):**

> "Let me tell you when Phase 1 makes sense. Imagine you're a small startup. You've got 3-5 developers, no dedicated DBA, and you need to ship an AI feature fast. You don't have time to set up complex infrastructure."

> "Phase 1 is perfect for this situation. Here's why:"

**Pros:**

> "First, it's dead simple. Your developers already know SQL. There's no new protocol to learn, no extra services to deploy. You write a query, you get results."

> "Second, there's no infrastructure overhead. The RDS Data API is serverless. You don't need to manage connection pools, worry about connection limits, or set up additional servers. It just works."

> "Third, debugging is straightforward. When something goes wrong, you can see exactly what SQL query ran. You can copy that query, paste it into your database tool, and figure out what happened."

> "Fourth, it's cost-effective for low volume. You're not paying for extra services or compute. Just your database and your application."

**Cons:**

> "But there are trade-offs. First, your AI code is tightly coupled to your database. If you want to switch databases later, you're rewriting a lot of code."

> "Second, every agent needs its own database connection logic. If you have multiple AI features, you're duplicating code."

> "Third, there's no standardization. Different developers might implement database access differently, making the codebase harder to maintain."

> "Fourth, and this is the big one, you're limited to keyword matching. The AI can only find things that match the exact words in your query. It doesn't understand intent."

**Bottom Line:**

> "Phase 1 is great for getting started, for MVPs, and for applications where keyword search is good enough. Most teams start here, and that's exactly right. Don't over-engineer on day one."

---

## Part 3: Phase 2 - MCP Abstraction Layer (15 minutes)

### What to Say:

**Click on Phase 2 in the UI**

> "Phase 2 introduces the Model Context Protocol, or MCP. This is an open standard created to provide a consistent way for AI models to interact with external tools and data sources."

> "Think of MCP as a universal adapter. Instead of writing custom code to connect your AI agent to every different database or service, you use MCP as a standard interface."

### Demo Query 1: Same Query, Different Architecture

**Type in the chat:** `running shoes`

> "Let me run the same query we did in Phase 1. I'll search for 'running shoes'."

**Point to the Activity Panel:**

> "Look at the activities now. They're different:"
>
> - "'Processing with MCP (postgres-mcp-server)' - we're using the MCP protocol"
> - "'MCP: connect_to_database' - the MCP server is handling the connection"
> - "'MCP: run_query' - the query goes through MCP"
> - "'MCP: Query completed' - same results, different path"

> "We got the same 4 products, but now the database access is going through a standardized protocol."

### Why MCP Matters

> "You might be wondering, why add this extra layer? Here's why MCP is valuable:"

> "First, it's portable. Your agent code doesn't change when you switch databases. The MCP server handles the specifics."

> "Second, it's standardized. Multiple AI frameworks can use the same MCP server. You're not locked into one vendor's approach."

> "Third, it provides better security and access control. The MCP server can enforce policies about what queries are allowed."

> "Fourth, it scales better. Multiple agents can share the same MCP server, and you can add caching, rate limiting, and other features at the MCP layer."

### Code Walkthrough (Optional):

**Open `backend/mcp/mcp_client.py` and scroll to line 159:**

> "Let me show you the MCP client code. This is the connect_to_database method starting at line 159."

> "You can see it's calling the MCP server's connect_to_database tool with parameters like database name, connection method, and cluster identifier."

**Scroll to line 195:**

> "And here's run_query at line 195. It sends the SQL query to the MCP server, which executes it and returns the results."

> "The key thing is that this is a standard interface. The awslabs.postgres-mcp-server we're using implements this interface for Aurora PostgreSQL, but there are MCP servers for many different data sources."

### Demo Query 2: Another Search

**Type in the chat:** `Nike training shoes`

> "Let me do another search to show it's working consistently. 'Nike training shoes'."

> "Same MCP flow, same reliable results. The abstraction layer is doing its job."

### Real-World Pros and Cons of Phase 2

**When to use this approach (The Story):**

> "Now let me tell you when Phase 2 makes sense. Imagine your startup has grown. You now have 15-20 developers, maybe a small platform team. You're building multiple AI features - a shopping assistant, a customer support bot, maybe an internal knowledge search."

> "Each of these features needs database access. And you're starting to see problems:"
>
> - "Different teams are implementing database connections differently"
> - "You want to add logging and monitoring, but you'd have to add it everywhere"
> - "Your CTO is asking about switching AI frameworks, and you realize you're locked in"

> "This is when MCP starts to make sense."

**Pros:**

> "First, standardization. Every AI agent uses the same interface to talk to the database. New developers can look at any agent and understand how it accesses data."

> "Second, portability. Your agent code doesn't know or care that it's talking to Aurora PostgreSQL. Tomorrow you could swap in a different database, and your agent code doesn't change."

> "Third, centralized concerns. Want to add query logging? Add it to the MCP server once. Want to enforce rate limits? Same place. Want to add caching? You get the idea."

> "Fourth, security boundaries. The MCP server can enforce what queries are allowed. You can prevent agents from running dangerous queries without modifying every agent."

> "Fifth, it's an open standard. MCP isn't proprietary. You're not locked into one vendor. There's a growing ecosystem of MCP servers for different data sources."

**Cons:**

> "But there are trade-offs here too. First, it's another moving part. You now have an MCP server to deploy, monitor, and maintain. That's operational overhead."

> "Second, there's a learning curve. Your team needs to understand MCP concepts - tools, resources, the protocol itself."

> "Third, debugging is one step removed. When something goes wrong, you're looking at MCP logs, not just SQL queries."

> "Fourth, it's still keyword search. You've improved your architecture, but you haven't improved your search quality. Users still can't ask natural language questions."

**Bottom Line:**

> "Phase 2 is about growing up architecturally. It's for teams that are scaling, that have multiple AI features, that care about maintainability and portability. If you're a single developer building one feature, this might be overkill. But if you're building a platform, MCP is worth the investment."

---

## Part 4: Phase 3 - Multi-Agent Orchestration with Hybrid Search (20 minutes)

### What to Say:

**Click on Phase 3 in the UI**

> "Now we get to the exciting part. Phase 3 introduces two major upgrades: multi-agent orchestration and semantic search using pgvector."

> "This is where we see a real production architecture. Instead of one agent doing everything, we have a Supervisor that delegates to specialized agents."

### Multi-Agent Architecture

> "Let me explain the architecture first:"

> "We have a SupervisorAgent that receives all requests. It doesn't do the work itself - it routes requests to the right specialized agent."

> "For search, we have a SearchAgent that handles all the embedding generation and hybrid search logic. In a full system, you'd also have a ProductAgent for inventory and an OrderAgent for transactions."

> "This is the supervisor pattern. It's how you scale AI systems - by breaking them into specialized components that each do one thing well."

### How the Search Works

> "When you type a query, here's what happens:"

> "First, the SupervisorAgent receives your request and decides which agent should handle it. For a search query, it delegates to the SearchAgent."

> "The SearchAgent then generates an embedding - a 1024-dimensional vector that captures the meaning of your query. We use Amazon Nova Multimodal Embeddings for this."

> "Then it runs a hybrid search combining:"
>
> - "Semantic search using pgvector - finds products whose embeddings are similar to your query"
> - "Lexical search using PostgreSQL's tsvector/tsrank - traditional full-text matching"

> "We weight semantic at 70% and lexical at 30%, then the SearchAgent returns the ranked results back to the Supervisor."

### Demo Query 1: Watch the Multi-Agent Flow

**Type in the chat:** `gear for my first marathon`

> "Let me show you this in action. Watch the Activity Panel carefully."

**Point to the Activity Panel and walk through each step:**

> "See the flow:"
>
> 1. "'Processing with Hybrid Search' - SupervisorAgent receives the request"
> 2. "'Delegating to SearchAgent' - Supervisor routes to the specialized agent"
> 3. "'Generating query embedding' - SearchAgent creates the vector"
> 4. "'Embedding generated' - Vector is ready"
> 5. "'Hybrid search: Semantic + Lexical' - SearchAgent runs both searches"
> 6. "'pgvector HNSW + tsrank search' - The actual database query"
> 7. "'SearchAgent returned 5 results' - Results flow back to Supervisor"

> "This is multi-agent orchestration in action. The Supervisor delegates, the SearchAgent does the specialized work, and results flow back up."

### Demo Query 2: Intent-Based Search

**Type in the chat:** `something to help with muscle recovery after workouts`

> "Let me try something more abstract. I'll search for 'something to help with muscle recovery after workouts'."

> "Look at the results. We got foam rollers, recovery products, massage tools. The AI understood the intent. I didn't say 'foam roller' or 'massage'. I described what I needed, and it found the right products."

> "This is the power of semantic search combined with multi-agent architecture."

### Comparison Demo

> "Let me show you the difference directly."

**Switch to Phase 1**

**Type:** `gear for my first marathon`

> "In Phase 1, this returns zero results. Keyword search can't understand 'marathon training'."

**Switch to Phase 3**

**Type:** `gear for my first marathon`

> "In Phase 3, the SearchAgent understands you're preparing for a marathon. It finds running shoes, training gear, and recovery products - all semantically related to marathon preparation."

> "That's the combination of multi-agent orchestration and semantic search."

### Code Walkthrough (Optional):

**Open `backend/routers/chat.py` and scroll to line 407:**

> "Let me show you the Phase 3 code. This is phase3_search starting at line 407."

**Scroll to around line 440:**

> "Here's where we generate the embedding using the embedding service."

**Scroll to around line 470:**

> "And here's the hybrid SQL query. You can see the WITH clause that does both semantic and lexical search, then combines the scores."

**Open `backend/db/embedding_service.py` and scroll to line 54:**

> "This is the embedding service. The generate_text_embedding method calls Amazon Bedrock with the Nova model to create the vector representation."

### Real-World Pros and Cons of Phase 3

**When to use this approach (The Story):**

> "Let me paint the picture for when Phase 3 becomes essential. Your company has product-market fit. You have real users, and they're complaining."

> "They say things like: 'I searched for comfortable running shoes but got hiking boots.' Or: 'I typed what I needed but got no results.' Or my favorite: 'Your search is useless, I just browse by category instead.'"

> "You look at your search analytics and see that 40% of searches return zero results. Users are typing natural language queries, and your keyword search can't handle them."

> "Plus, your single agent is getting overloaded. It's handling search, inventory, orders, customer support - everything. It's becoming a bottleneck."

> "This is when you need multi-agent orchestration and semantic search. This is Phase 3."

**Pros:**

> "First, the multi-agent architecture scales. Each agent is specialized - SearchAgent handles search, ProductAgent handles inventory, OrderAgent handles transactions. You can optimize, scale, and debug each one independently."

> "Second, semantic search actually understands what users mean. When someone types 'comfortable shoes for long runs', it knows they want cushioned running shoes. That's a game-changer for user experience."

> "Third, it handles the long tail. Users don't always use the exact words in your product catalog. Semantic search bridges that gap."

> "Fourth, you get the best of both worlds with hybrid search. Exact keyword matches still rank highly, but semantic understanding fills in the gaps."

> "Fifth, it's all in PostgreSQL. You don't need a separate vector database. pgvector is an extension to the database you're already running. One database, one backup strategy, one operational model."

**Cons:**

> "But this is the most complex approach, and there are real trade-offs."

> "First, orchestration complexity. You now have multiple agents to coordinate. The Supervisor needs to route correctly, handle failures, and aggregate results."

> "Second, latency. Generating embeddings takes time - typically 200-300ms per query. You need to think about caching strategies for common queries."

> "Third, cost. You're calling an embedding model for every search. At high volume, those API calls add up. You need to budget for it."

> "Fourth, you need to embed your product catalog. Every product needs an embedding stored in the database. That's a data pipeline you need to build and maintain."

> "Fifth, debugging is harder. When something goes wrong, you're tracing through multiple agents and vector similarity scores. It requires different skills."

**Bottom Line:**

> "Phase 3 is for when you need both scale and intelligence. The multi-agent architecture lets you scale horizontally - add more specialized agents as your system grows. The semantic search lets you understand user intent."

> "E-commerce, customer support, content discovery - anywhere users are expressing intent in natural language and you need to handle high volume. It's more complex, but the combination of multi-agent orchestration and semantic search is how production AI systems are built."

---

## Part 5: Order Processing (5 minutes)

### What to Say:

> "Let's complete the e-commerce flow by placing an order."

**Search for a product in any phase, then click the Order button on a product**

> "I'll click Order on this product."

**Show the order confirmation:**

> "You can see the order was processed. We have an order ID, the product details, pricing with tax and shipping, and a confirmed status."

> "The order processing works the same way across all three phases. The agent handles inventory checks, calculates pricing, and confirms the order."

---

## Part 6: Architecture Summary (5 minutes)

### What to Say:

> "Let me summarize what we've seen today."

**Draw or show this comparison:**

|                        | Phase 1             | Phase 2         | Phase 3                |
| ---------------------- | ------------------- | --------------- | ---------------------- |
| **Architecture**       | Single Agent        | Single Agent    | Multi-Agent Supervisor |
| **Connection**         | Direct RDS Data API | MCP Protocol    | MCP + pgvector         |
| **Search**             | Keyword/SQL         | Keyword/SQL     | Semantic + Lexical     |
| **Understands Intent** | No                  | No              | Yes                    |
| **Complexity**         | Low                 | Medium          | High                   |
| **Best For**           | Getting started     | Standardization | Production AI systems  |

### When to Use Each Phase

> "So when should you use each approach?"

> "Phase 1 is perfect for getting started. If you're building a prototype or MVP, or if your queries are straightforward, direct database access is simple and effective."

> "Phase 2 makes sense when you need portability and standardization. If you have multiple AI agents, or you want to switch between different AI frameworks, MCP provides that abstraction."

> "Phase 3 is for production AI systems that need both scale and intelligence. The multi-agent architecture lets you scale horizontally with specialized agents. The semantic search lets you understand user intent. Together, they're how you build AI systems that can handle real-world complexity."

> "The good news is you can start with Phase 1 and evolve. These aren't mutually exclusive. Many teams start simple and add multi-agent orchestration and semantic search when they need it."

---

## Part 7: Q&A and Wrap-up (5 minutes)

### Key Takeaways to Emphasize:

> "Before we open for questions, let me leave you with four key points:"

> "First, Aurora PostgreSQL is a powerful foundation for agentic AI. With pgvector, you get semantic search built right into your database. No separate vector database needed."

> "Second, MCP provides a standard way to connect AI agents to data. It's an open protocol that makes your architecture more portable and maintainable."

> "Third, multi-agent orchestration is how you scale AI systems. The supervisor pattern lets you break complex tasks into specialized agents that each do one thing well."

> "Fourth, start simple and evolve. You don't need to build Phase 3 on day one. Start with direct database access, add MCP when you need standardization, and add multi-agent orchestration with semantic search when you need production scale."

### Resources:

> "If you want to learn more:"
>
> - "Aurora PostgreSQL documentation on AWS"
> - "pgvector on GitHub"
> - "Model Context Protocol at modelcontextprotocol.io"
> - "The awslabs.postgres-mcp-server on GitHub"

> "Thank you for your time. I'm happy to take questions."

---

## Backup Queries

If you need additional queries during the demo:

**Phase 1/2 (Keyword searches that work well):**

- `running shoes` - matches category
- `Nike` - matches brand
- `recovery products` - matches category keyword
- `accessories under $50` - category + price filter
- `fitness equipment` - matches category

**Phase 1/2 (Semantic queries that FAIL - show the limitation):**

- `gear for my first marathon` - returns 0 results
- `help me build core strength` - returns 0 results
- `track my fitness progress` - returns 0 results
- `relieve sore muscles` - returns 0 results
- `something comfortable for long runs` - returns 0 results

**Phase 1/2 (Semantic queries that ACCIDENTALLY work - show inconsistency):**

- `breathable clothes for hot weather` - returns results (matches "clothes" keyword)
- `comfortable running shoes` - returns results (matches "running shoes" keyword)

**Phase 3 (Semantic searches that show the difference):**

- `gear for my first marathon` - finds running shoes, apparel, recovery
- `help me build core strength` - finds fitness equipment
- `relieve sore muscles after gym` - finds recovery products
- `track my fitness progress` - finds watches and accessories
- `shoes with good arch support` - finds cushioned running shoes

---

## Troubleshooting

**If the backend stops responding:**

```bash
# Check if it's running
curl http://localhost:8000/api/products?limit=1


# Restart if needed
pkill -f uvicorn
cd clickshop-demo
source venv/bin/activate
uvicorn backend.main:app --reload --port 8000
```

**If the frontend won't load:**

```bash
cd clickshop-demo/frontend
npm run dev
```

**If Phase 3 is slow:**

- The first query takes 2-3 seconds because it generates embeddings
- Subsequent queries are faster
- Say: "The embedding generation is a one-time cost per query. In production, you'd cache common queries."

**If you get no results:**

- Check that you're searching for products that exist (running shoes, fitness equipment, recovery, apparel, accessories)
- Try a simpler query first to verify the system is working
