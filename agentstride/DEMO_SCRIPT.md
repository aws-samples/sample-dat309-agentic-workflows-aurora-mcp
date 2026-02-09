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
cd agentstride
source venv/bin/activate
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**

```bash
cd agentstride/frontend
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

## Tested Query Reference & Talking Points

All queries below have been tested and verified against the live backend.

---

### Phase 1 — Direct RDS Data API

**Architecture:** Single `Phase1Agent` with 5 `@tool` decorators, direct connection to Aurora PostgreSQL via RDS Data API.

**Key talking points:**

- Simplest approach — agent writes SQL, executes via HTTP, returns results
- Serverless-friendly (no connection pools, no timeouts)
- Great for MVPs and getting started fast
- Limitation: keyword matching only (ILIKE). No semantic understanding of user intent
- Demo the inconsistency: `gear for my first marathon` → 0 results, but `breathable clothes for hot weather` → results (because "clothes" accidentally matches the Apparel category keyword)

**Queries that work (verified):**

| Query                   | Results | Why it works                                  |
| ----------------------- | ------- | --------------------------------------------- |
| `running shoes`         | 4       | Matches "Running Shoes" category keyword      |
| `Nike shoes`            | 5       | "shoes" triggers shoe category search         |
| `shoes under $150`      | 5       | "shoes" + price filter `<= 150`               |
| `fitness equipment`     | 5       | Matches "Fitness Equipment" category keyword  |
| `Nike`                  | 5       | ILIKE brand match                             |
| `recovery products`     | 5       | Matches "Recovery" category keyword           |
| `accessories under $50` | 1       | Matches "Accessories" category + price filter |

**Queries that fail — by design (verified):**

| Query                                 | Results | Why it fails                                      |
| ------------------------------------- | ------- | ------------------------------------------------- |
| `gear for my first marathon`          | 0       | No keyword match for "marathon" or "gear"         |
| `help me build core strength`         | 0       | No keyword match for "core strength"              |
| `relieve sore muscles`                | 0       | No keyword match for "sore muscles"               |
| `something comfortable for long runs` | 0       | No keyword match for "comfortable" or "long runs" |
| `track my fitness progress`           | 0       | No keyword match for "fitness progress"           |

**Queries that accidentally work (show inconsistency):**

| Query                                | Results | Why it accidentally works                      |
| ------------------------------------ | ------- | ---------------------------------------------- |
| `breathable clothes for hot weather` | 5       | "clothes" matches Apparel category keyword     |
| `comfortable running shoes`          | 4       | "running shoes" matches Running Shoes category |

---

### Phase 2 — MCP Abstraction Layer

**Architecture:** Single `Phase2Agent` with `MCPClient` connecting to `awslabs.postgres-mcp-server`. Tools auto-discovered from the MCP server.

**Key talking points:**

- Same search capability as Phase 1 (still keyword-based)
- The upgrade is architectural: standardized interface via Model Context Protocol
- Portable — swap databases without changing agent code
- Centralized concerns — logging, rate limiting, security at the MCP layer
- Open standard, growing ecosystem
- Trade-off: extra moving part (MCP server to deploy/monitor), learning curve
- Best for teams scaling to multiple AI features that need standardization

**Queries that work (verified):**

| Query                  | Results | Why it works                                       |
| ---------------------- | ------- | -------------------------------------------------- |
| `running shoes`        | 4       | Matches "Running Shoes" category keyword           |
| `Nike training shoes`  | 5       | "training shoes" matches Training Shoes category   |
| `fitness equipment`    | 5       | Matches "Fitness Equipment" category keyword       |
| `recovery products`    | 5       | Matches "Recovery" category keyword                |
| `Brooks running shoes` | 4       | "running shoes" matches category (no Brooks in DB) |

**Queries that fail — by design (verified):**

| Query                         | Results | Why it fails                                  |
| ----------------------------- | ------- | --------------------------------------------- |
| `gear for my first marathon`  | 0       | No keyword match — same limitation as Phase 1 |
| `Help me build core strength` | 0       | No keyword match for "core strength"          |
| `Help with foot pain`         | 0       | No keyword match for "foot pain"              |

---

### Phase 3 — Multi-Agent Orchestration + Hybrid Search

**Architecture:** `SupervisorAgent` (delegation only) → `SearchAgent` (semantic + lexical), `ProductAgent` (inventory), `OrderAgent` (transactions). Uses Nova Multimodal embeddings (1024d) stored in pgvector with HNSW index. Hybrid search: 70% semantic + 30% lexical (tsvector/tsrank).

**Key talking points:**

- Supervisor pattern — each agent has a single responsibility, supervisor orchestrates
- SearchAgent generates embeddings and runs hybrid search against pgvector
- Understands intent: `gear for my first marathon` → running shoes, apparel, recovery products
- All in PostgreSQL — no separate vector database needed (pgvector extension)
- ProductAgent handles inventory checks, OrderAgent handles transactions
- Trade-offs: orchestration complexity, embedding latency (~200-300ms), embedding cost at scale
- Best for production AI systems that need both scale and intelligence

#### SupervisorAgent → SearchAgent (Semantic Search — verified)

| Query                                                   | Results | Products returned                                                                          |
| ------------------------------------------------------- | ------- | ------------------------------------------------------------------------------------------ |
| `gear for my first marathon`                            | 5       | Garmin Forerunner 965, Nike Dri-FIT Shorts, Reebok Nano X4, Puma Fuse 3.0, Nike Pegasus 41 |
| `help me build core strength`                           | 5       | Peloton Guide, Foam Roller, Nike Metcon 9, Bowflex Dumbbells, Hyperice Normatec            |
| `relieve sore muscles after gym`                        | 5       | Epsom Salt Soak, Foam Roller, Nike Dri-FIT Shorts, Hyperice Normatec, Compex Sport Elite   |
| `track my fitness progress`                             | 5       | Peloton Guide, Garmin Forerunner 965, Beats Fit Pro, Apple Watch Ultra 2, TRX PRO4         |
| `shoes with good arch support`                          | 5       | Nike Blazer Mid, New Balance 1080v13, Nike Air Max 1, Puma Fuse 3.0, Nike Vomero 18        |
| `something to help with muscle recovery after workouts` | 5       | Foam Roller, Compex Sport Elite, Epsom Salt Soak, Hyperice Normatec, Reebok Nano X4        |

**Activity Panel shows:**

1. SupervisorAgent: "Delegating to SearchAgent"
2. SearchAgent: "Generating query embedding" (Nova Multimodal 1024d)
3. SearchAgent: "Hybrid search: Semantic + Lexical"
4. SearchAgent: "pgvector HNSW + tsrank search"
5. SupervisorAgent: "SearchAgent returned X results"

#### SupervisorAgent → ProductAgent (Inventory Check — verified)

| Query                                       | Result                                           |
| ------------------------------------------- | ------------------------------------------------ |
| `Is the Nike Pegasus in stock?`             | ✅ Nike Air Zoom Pegasus 41 — 66 units available |
| `Do you have the Garmin watch available?`   | ✅ Garmin Forerunner 965 — 15 units available    |
| `What sizes are available for Apple Watch?` | ✅ Apple Watch Ultra 2 — 49mm                    |
| `Check stock for Garmin watch`              | ✅ Garmin Forerunner 965 — 15 units available    |

**Activity Panel shows:**

1. SupervisorAgent: "Delegating to ProductAgent"
2. ProductAgent: "Finding product"
3. ProductAgent: "Checking inventory"
4. ProductAgent: "Stock verified"
5. SupervisorAgent: "ProductAgent returned to Supervisor"

#### SupervisorAgent → OrderAgent (Order Processing — verified)

Click the **Order** button on any product to see the OrderAgent.

**Activity Panel shows:**

1. SupervisorAgent: "Processing order request"
2. OrderAgent: "Looking up product details"
3. OrderAgent: "Checking inventory"
4. OrderAgent: "Calculating total"
5. OrderAgent: "Processing order"
6. SupervisorAgent: "OrderAgent completed"

#### Recommended Demo Sequence

1. **SearchAgent**: `gear for my first marathon` → Shows semantic search (5 results)
2. **ProductAgent**: `Is the Nike Pegasus in stock?` → Shows inventory check (66 units)
3. **OrderAgent**: Click Order on a product → Shows full order workflow with confirmation

> "Notice how the Supervisor delegates to different specialized agents based on the type of request. This is the supervisor pattern - each agent has a single responsibility, and the supervisor orchestrates them."

---

### Key Differentiator Summary

|                        | Phase 1             | Phase 2         | Phase 3                   |
| ---------------------- | ------------------- | --------------- | ------------------------- |
| **Connection**         | Direct RDS Data API | MCP Protocol    | MCP + pgvector            |
| **Architecture**       | Single Agent        | Single Agent    | Multi-Agent Supervisor    |
| **Search**             | Keyword/ILIKE       | Keyword/ILIKE   | Semantic + Lexical hybrid |
| **Understands intent** | No                  | No              | Yes                       |
| **Best for**           | Getting started     | Standardization | Production AI systems     |

**The narrative arc:** Start simple (Phase 1), standardize (Phase 2), add intelligence and scale (Phase 3). Each phase builds on the previous one.

---

## Troubleshooting

**If the backend stops responding:**

```bash
# Check if it's running
curl http://localhost:8000/api/products?limit=1


# Restart if needed
pkill -f uvicorn
cd agentstride
source venv/bin/activate
uvicorn backend.main:app --reload --port 8000
```

**If the frontend won't load:**

```bash
cd agentstride/frontend
npm run dev
```

**If Phase 3 is slow:**

- The first query takes 2-3 seconds because it generates embeddings
- Subsequent queries are faster
- Say: "The embedding generation is a one-time cost per query. In production, you'd cache common queries."

**If you get no results:**

- Check that you're searching for products that exist (running shoes, fitness equipment, recovery, apparel, accessories)
- Try a simpler query first to verify the system is working

---

## Technical Implementation Reference

This section documents the technical implementation of each phase for code walkthrough during the demo.

### Phase 1: Direct Database Access

**File:** `backend/agents/phase1/agent.py`

```python
# Strands SDK with Bedrock Model
from strands import Agent, tool
from strands.models import BedrockModel

class Phase1Agent:
    def __init__(self):
        self.model = BedrockModel(
            model_id="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
            region_name="us-east-1"
        )
        self.agent = Agent(
            model=self.model,
            tools=[self._lookup_product, self._search_products,
                   self._check_inventory, self._calculate_total,
                   self._process_order],
            system_prompt=self._get_system_prompt()
        )

    @tool
    async def _search_products(self, query: str, limit: int = 5):
        """Keyword-based product search using ILIKE."""
        sql = "SELECT ... FROM products WHERE name ILIKE %s"
        # Direct RDS Data API call
```

**Key Points:**

- Single agent with 5 tools
- Direct RDS Data API connection
- Keyword matching only (ILIKE queries)
- No semantic understanding

### Phase 2: MCP Abstraction Layer

**File:** `backend/agents/phase2/agent.py`

```python
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient

class Phase2Agent:
    def __init__(self):
        self.model = BedrockModel(...)

        # MCP client for postgres-mcp-server
        self.mcp_client = MCPClient(
            server_name="postgres-mcp-server",
            command="uvx",
            args=["awslabs.postgres-mcp-server@latest"]
        )

    async def _initialize_agent(self):
        await self.mcp_client.connect()
        mcp_tools = await self.mcp_client.list_tools()
        # Auto-discover tools from MCP server
        self.agent = Agent(model=self.model, tools=mcp_tools)
```

**Key Points:**

- Same keyword search capability as Phase 1
- Tools auto-discovered from MCP server
- Standardized interface via Model Context Protocol
- Still no semantic understanding

### Phase 3: Multi-Agent Orchestration with Hybrid Search

**Files:**

- `backend/agents/phase3/supervisor.py` - Orchestrator
- `backend/agents/phase3/search_agent.py` - Semantic search
- `backend/agents/phase3/product_agent.py` - Inventory
- `backend/agents/phase3/order_agent.py` - Orders

**SupervisorAgent (Orchestrator):**

```python
class SupervisorAgent:
    def __init__(self, search_agent, product_agent, order_agent):
        # Supervisor has delegation tools only (no direct DB access)
        self.agent = Agent(
            model=self.model,
            tools=[self._delegate_to_search,
                   self._delegate_to_product,
                   self._delegate_to_order]
        )
```

**SearchAgent (Semantic + Lexical):**

```python
class SearchAgent:
    def __init__(self):
        self.bedrock_runtime = boto3.client('bedrock-runtime')
        self.agent = Agent(
            model=self.model,
            tools=[self._semantic_search_tool, self._visual_search_tool]
        )

    @tool
    async def _semantic_search_tool(self, query: str, limit: int = 5):
        """Hybrid search: pgvector + tsvector/tsrank"""
        # Generate embedding with Nova Multimodal (1024d)
        embedding = self._generate_text_embedding(query)

        # Hybrid SQL: 70% semantic + 30% lexical
        sql = """
            WITH semantic_search AS (
                SELECT ..., 1 - (embedding <=> %s::vector) as semantic_score
            ),
            lexical_search AS (
                SELECT ..., ts_rank(...) as lexical_score
            )
            SELECT ... ORDER BY (0.7 * semantic + 0.3 * lexical) DESC
        """
```

**ProductAgent:**

```python
class ProductAgent:
    @tool
    async def _get_details_tool(self, product_id: str):
        """Get product details by ID."""

    @tool
    async def _check_inventory_tool(self, product_id: str, size: str = None):
        """Check inventory status."""
```

**OrderAgent:**

```python
class OrderAgent:
    @tool
    async def _calculate_total_tool(self, items: List[dict]):
        """Calculate order total with tax and shipping."""

    @tool
    async def _process_order_tool(self, customer_id: str, items: List[dict]):
        """Process and confirm order."""
```

**Key Points:**

- Supervisor pattern with specialized agents
- Each agent has focused tools
- SearchAgent uses Nova Multimodal embeddings (1024d)
- Hybrid search combines semantic (pgvector) + lexical (tsvector/tsrank)
- Cross-modal search: same vector space for text and images

---

## Demo Verification Queries

Use these queries to verify the progressive feature story across all three phases:

### Cross-Phase Comparison (the money shot)

| Query                                 | Phase 1   | Phase 2   | Phase 3   |
| ------------------------------------- | --------- | --------- | --------- |
| `running shoes`                       | 4 results | 4 results | 5 results |
| `Nike`                                | 5 results | 5 results | 5 results |
| `Nike shoes`                          | 5 results | 5 results | 5 results |
| `shoes under $150`                    | 5 results | 5 results | 5 results |
| `fitness equipment`                   | 5 results | 5 results | 5 results |
| `gear for my first marathon`          | 0 results | 0 results | 5 results |
| `help me build core strength`         | 0 results | 0 results | 5 results |
| `relieve sore muscles`                | 0 results | 0 results | 5 results |
| `track my fitness progress`           | 0 results | 0 results | 5 results |
| `something comfortable for long runs` | 0 results | 0 results | 5 results |

The keyword queries work across all phases. The semantic queries fail in Phase 1/2 (keyword search) but succeed in Phase 3 (hybrid search with embeddings). This is the core story of the demo.

### Phase 3 ProductAgent Verification

| Query                                       | Agent        | Result                |
| ------------------------------------------- | ------------ | --------------------- |
| `Is the Nike Pegasus in stock?`             | ProductAgent | ✅ 66 units available |
| `Do you have the Garmin watch available?`   | ProductAgent | ✅ 15 units available |
| `What sizes are available for Apple Watch?` | ProductAgent | ✅ 49mm               |
| `Check stock for Garmin watch`              | ProductAgent | ✅ 15 units available |

### Phase 3 OrderAgent Verification

| Action                       | Agent      | Result                                   |
| ---------------------------- | ---------- | ---------------------------------------- |
| Click "Order" on any product | OrderAgent | ✅ Full order workflow with confirmation |

---

## Appendix A: Agent Implementation Quick Reference

### Phase 1: Direct RDS Data API

| Component | Agent Name    | File Path                        | Strands Tools                                     |
| --------- | ------------- | -------------------------------- | ------------------------------------------------- |
| Search    | `Phase1Agent` | `backend/agents/phase1/agent.py` | `@tool _search_products()` - ILIKE keyword search |
| Order     | `Phase1Agent` | `backend/agents/phase1/agent.py` | `@tool _process_order()`                          |

**Demo Query:** `gear for my first marathon` → **0 results** (keyword search fails)

**Activity Panel Shows:**

```
Phase1Agent: Processing with Direct RDS Data API
Phase1Agent: Direct RDS Data API connection
Phase1Agent: Text search: gear for my first marathon (ILIKE query)
Phase1Agent: Found 0 products
```

**Key Code (line ~250):**

```python
sql = "SELECT ... FROM products WHERE (name ILIKE %s OR description ILIKE %s)"
```

---

### Phase 2: MCP Abstraction Layer

| Component | Agent Name    | File Path                        | Strands Tools                           |
| --------- | ------------- | -------------------------------- | --------------------------------------- |
| Search    | `Phase2Agent` | `backend/agents/phase2/agent.py` | MCP: `connect_to_database`, `run_query` |
| Order     | `Phase2Agent` | `backend/agents/phase2/agent.py` | MCP tools (auto-discovered)             |

**Demo Query:** `gear for my first marathon` → **0 results** (still keyword search)

**Activity Panel Shows:**

```
Phase2Agent: Processing with MCP (postgres-mcp-server)
Phase2Agent: MCP: connect_to_database
Phase2Agent: MCP: run_query (ILIKE query)
Phase2Agent: MCP: Query completed - 0 rows
```

**Key Code (line ~70):**

```python
self.mcp_client = MCPClient(
    server_name="postgres-mcp-server",
    command="uvx",
    args=["awslabs.postgres-mcp-server@latest"]
)
mcp_tools = await self.mcp_client.list_tools()  # Auto-discover tools
```

---

### Phase 3: Multi-Agent Orchestration with Hybrid Search

#### SupervisorAgent (Orchestrator)

| Agent Name        | File Path                             | Role                                  |
| ----------------- | ------------------------------------- | ------------------------------------- |
| `SupervisorAgent` | `backend/agents/phase3/supervisor.py` | Routes requests to specialized agents |

**Tools:** Delegation only (no direct DB access per requirement 11.5)

- `_delegate_to_search()` → SearchAgent
- `_delegate_to_product()` → ProductAgent
- `_delegate_to_order()` → OrderAgent

---

#### SearchAgent (Semantic + Lexical Search)

| Agent Name    | File Path                               | Strands Tools                                                  |
| ------------- | --------------------------------------- | -------------------------------------------------------------- |
| `SearchAgent` | `backend/agents/phase3/search_agent.py` | `@tool _semantic_search_tool()`, `@tool _visual_search_tool()` |

**Demo Query:** `gear for my first marathon` → **5 results** (semantic understanding!)

**Activity Panel Shows:**

```
SupervisorAgent: Processing with Hybrid Search (Semantic + Lexical)
SupervisorAgent: Delegating to SearchAgent
SearchAgent: Generating query embedding (Nova Multimodal 1024d)
SearchAgent: Embedding generated (482ms)
SearchAgent: Hybrid search: Semantic + Lexical (pgvector + tsvector)
SearchAgent: pgvector HNSW + tsrank search - Found 5 products
SupervisorAgent: SearchAgent returned 5 results
```

**Key Code (line ~180):**

```python
# Generate embedding with Nova Multimodal
query_embedding = self._generate_text_embedding(query)

# Hybrid SQL: 70% semantic + 30% lexical
sql = """
    WITH semantic_search AS (
        SELECT ..., 1 - (embedding <=> %s::vector) as semantic_score
    ),
    lexical_search AS (
        SELECT ..., ts_rank(...) as lexical_score
    )
    SELECT ... ORDER BY (0.7 * semantic + 0.3 * lexical) DESC
"""
```

---

#### ProductAgent (Inventory & Details)

| Agent Name     | File Path                                | Strands Tools                                                |
| -------------- | ---------------------------------------- | ------------------------------------------------------------ |
| `ProductAgent` | `backend/agents/phase3/product_agent.py` | `@tool _get_details_tool()`, `@tool _check_inventory_tool()` |

**Demo Query:** `Is the Nike Pegasus in stock?` → Shows inventory check

**Activity Panel Shows:**

```
SupervisorAgent: Processing with Multi-Agent Orchestration
SupervisorAgent: Delegating to ProductAgent
ProductAgent: Finding product
ProductAgent: Checking inventory (SQL query)
ProductAgent: Stock verified - 66 units available
SupervisorAgent: ProductAgent returned to Supervisor
```

**Key Code (line ~110):**

```python
@tool
async def _check_inventory_tool(self, product_id: str, size: str = None):
    query = "SELECT inventory, available_sizes FROM products WHERE product_id = %s"
```

---

#### OrderAgent (Order Processing)

| Agent Name   | File Path                              | Strands Tools                                                  |
| ------------ | -------------------------------------- | -------------------------------------------------------------- |
| `OrderAgent` | `backend/agents/phase3/order_agent.py` | `@tool _calculate_total_tool()`, `@tool _process_order_tool()` |

**Demo Action:** Click "Order" button on any product

**Activity Panel Shows:**

```
OrderAgent: Looking up product details
OrderAgent: Found: Nike Air Zoom Pegasus 41
OrderAgent: Checking inventory
OrderAgent: In Stock - 46 units
OrderAgent: Processing payment
OrderAgent: Payment authorized
OrderAgent: Order confirmed
OrderAgent: Order complete
```

**Key Code (line ~150):**

```python
@tool
async def _process_order_tool(self, customer_id: str, items: List[dict]):
    # Calculate totals, insert order, insert order items
    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    await self.db.execute("INSERT INTO orders ...")
```

---

## Appendix B: Demo Flow Cheat Sheet

### Recommended Demo Sequence

1. **Phase 1 - Show Limitation**

   ```
   Query: "gear for my first marathon"
   Result: 0 products (keyword search fails)
   Point: "Phase 1 can't understand semantic intent"
   ```

2. **Phase 2 - Same Result, Better Architecture**

   ```
   Query: "gear for my first marathon"
   Result: 0 products (still keyword search)
   Point: "MCP provides abstraction, but search is still keyword-based"
   ```

3. **Phase 3 - Semantic Understanding**

   ```
   Query: "gear for my first marathon"
   Result: 5 products (running shoes, apparel, accessories)
   Point: "Hybrid search understands marathon training intent"
   ```

4. **Phase 3 - ProductAgent Demo**

   ```
   Query: "Is the Nike Pegasus in stock?"
   Result: 66 units available (sizes: 7, 7.5, 8, 8.5, 9)
   Point: "Supervisor delegates to specialized ProductAgent"
   ```

5. **Phase 3 - ProductAgent Demo (Garmin)**

   ```
   Query: "Do you have the Garmin watch available?"
   Result: 15 units available (One Size)
   Point: "ProductAgent handles any inventory lookup"
   ```

6. **Phase 3 - OrderAgent Demo**
   ```
   Action: Click "Order" on any product
   Result: Full order workflow with confirmation
   Point: "OrderAgent handles the complete transaction"
   ```

### Quick Test Commands

```bash
# Phase 1 - Keyword search (fails for semantic)
curl -s -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "gear for my first marathon", "phase": 1}'

# Phase 2 - MCP abstraction (still fails)
curl -s -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "gear for my first marathon", "phase": 2}'

# Phase 3 - Hybrid search (succeeds!)
curl -s -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "gear for my first marathon", "phase": 3}'

# Phase 3 - ProductAgent (inventory check)
curl -s -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Is the Nike Pegasus in stock?", "phase": 3}'

# Phase 3 - OrderAgent (place order)
curl -s -X POST http://localhost:8000/api/chat/order \
  -H "Content-Type: application/json" \
  -d '{"product_id": "RUN-001", "size": "10", "quantity": 1, "phase": 3}'
```

### Key Files to Show During Code Walkthrough

| Phase | File                                     | Key Lines | What to Show                     |
| ----- | ---------------------------------------- | --------- | -------------------------------- |
| 1     | `backend/agents/phase1/agent.py`         | 92-120    | `@tool` decorators, ILIKE search |
| 2     | `backend/agents/phase2/agent.py`         | 70-95     | MCPClient setup, auto-discovery  |
| 3     | `backend/agents/phase3/supervisor.py`    | 60-90     | Delegation pattern               |
| 3     | `backend/agents/phase3/search_agent.py`  | 130-180   | Nova embeddings, hybrid SQL      |
| 3     | `backend/agents/phase3/product_agent.py` | 100-130   | Inventory tools                  |
| 3     | `backend/agents/phase3/order_agent.py`   | 140-180   | Order processing                 |
