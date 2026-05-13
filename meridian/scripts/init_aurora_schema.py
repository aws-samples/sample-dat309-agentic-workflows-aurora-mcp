"""
Initialize Aurora PostgreSQL database schema for Meridian 2026 Refresh
Includes pgvector for semantic and visual search with Cohere Embed v4 embeddings (1024 dimensions)

Requirements covered:
- 1.1: Product catalog with consumer electronics/smart home domain
- 1.3: Product fields including JSONB for variants, inventory, specifications, compatibility
- 3.1: Memory schema (conversations, preferences, interaction_embeddings) for Phase 4
- 5.1: pgvector HNSW index with improved recall and pre-filtering support
- 5.2: JSONB capabilities for product specifications, compatibility, and agent memory
- 5.3: Generated tsvector column for full-text search optimization
- 8.1: agent_traces table for token usage tracking (input/output tokens per agent invocation)
- 8.2: agent_traces table for latency waterfall tracking (total_latency_ms, nested traces)
- 8.4: agent_traces table for cost estimation per interaction (estimated_cost_usd)
"""
import os
import boto3
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv()
console = Console()

# Get RDS Data API configuration
CLUSTER_ARN = os.getenv('AURORA_CLUSTER_ARN')
SECRET_ARN = os.getenv('AURORA_SECRET_ARN')
DATABASE = os.getenv('AURORA_DATABASE', 'meridian')
REGION = os.getenv('BEDROCK_REGION', 'us-east-1')


def execute_sql(client, sql: str, description: str = ""):
    """Execute SQL using RDS Data API"""
    try:
        response = client.execute_statement(
            resourceArn=CLUSTER_ARN,
            secretArn=SECRET_ARN,
            database=DATABASE,
            sql=sql
        )
        if description:
            console.print(f"[green]✅ {description}[/green]")
        return response
    except Exception as e:
        console.print(f"[red]❌ Error executing SQL: {e}[/red]")
        raise


def initialize_database():
    """Initialize Aurora database with refreshed schema for Meridian 2026 using RDS Data API"""
    console.print("\n[bold blue]🚀 Initializing Aurora PostgreSQL Database for Meridian 2026[/bold blue]")
    console.print(f"Cluster ARN: {CLUSTER_ARN}")
    console.print(f"Database: {DATABASE}\n")

    if not CLUSTER_ARN or not SECRET_ARN:
        console.print("[red]❌ Missing AURORA_CLUSTER_ARN or AURORA_SECRET_ARN in .env[/red]")
        return

    try:
        # Create RDS Data API client
        client = boto3.client('rds-data', region_name=REGION)

        # --- Drop existing tables for clean reinstall ---
        console.print("[yellow]Dropping existing tables...[/yellow]")
        drop_statements = [
            ("DROP TABLE IF EXISTS order_items CASCADE", "Dropped order_items"),
            ("DROP TABLE IF EXISTS orders CASCADE", "Dropped orders"),
            ("DROP TABLE IF EXISTS customers CASCADE", "Dropped customers"),
            ("DROP TABLE IF EXISTS products CASCADE", "Dropped products"),
            ("DROP TABLE IF EXISTS agent_analytics CASCADE", "Dropped agent_analytics"),
            ("DROP TABLE IF EXISTS inventory_transactions CASCADE", "Dropped inventory_transactions"),
        ]

        for sql, desc in drop_statements:
            execute_sql(client, sql, desc)

        # --- Enable extensions ---
        console.print("\n[yellow]Enabling extensions...[/yellow]")
        execute_sql(client, "CREATE EXTENSION IF NOT EXISTS vector", "pgvector extension enabled")

        # --- Create refreshed products table ---
        # Requirement 1.3: product_id, name, category, price, brand, description, image_url,
        #   available_variants (JSONB), inventory (JSONB), specifications (JSONB),
        #   compatibility (JSONB), embedding vector(1024), search_vector (generated tsvector)
        # Requirement 5.3: Generated tsvector column auto-generated from name, description, brand
        console.print("\n[yellow]Creating products table with JSONB fields and generated tsvector...[/yellow]")
        products_sql = """
        CREATE TABLE products (
            product_id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            category VARCHAR(100) NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            brand VARCHAR(100),
            description TEXT,
            image_url VARCHAR(500),
            available_sizes JSONB,
            available_variants JSONB,
            inventory JSONB NOT NULL,
            specifications JSONB,
            compatibility JSONB,
            embedding vector(1024),
            search_vector tsvector GENERATED ALWAYS AS (
                to_tsvector('english', name || ' ' || COALESCE(description, '') || ' ' || COALESCE(brand, ''))
            ) STORED,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        execute_sql(client, products_sql, "Created products table with JSONB fields and generated search_vector")

        # --- Create customers table ---
        customers_sql = """
        CREATE TABLE customers (
            customer_id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        execute_sql(client, customers_sql, "Created customers table")

        # --- Create orders table ---
        orders_sql = """
        CREATE TABLE orders (
            order_id VARCHAR(50) PRIMARY KEY,
            customer_id VARCHAR(50) REFERENCES customers(customer_id),
            status VARCHAR(50) DEFAULT 'pending',
            total_amount DECIMAL(10, 2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )
        """
        execute_sql(client, orders_sql, "Created orders table")

        # --- Create order_items table ---
        order_items_sql = """
        CREATE TABLE order_items (
            item_id SERIAL PRIMARY KEY,
            order_id VARCHAR(50) REFERENCES orders(order_id),
            product_id VARCHAR(50) REFERENCES products(product_id),
            size VARCHAR(10),
            quantity INTEGER DEFAULT 1,
            unit_price DECIMAL(10, 2) NOT NULL
        )
        """
        execute_sql(client, order_items_sql, "Created order_items table")

        # --- Create indexes ---
        console.print("\n[yellow]Creating indexes...[/yellow]")

        # HNSW index for vector similarity search
        # Requirement 5.1: pgvector HNSW index with m=16, ef_construction=100
        hnsw_sql = """
        CREATE INDEX idx_products_embedding_hnsw ON products
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 100)
        """
        execute_sql(client, hnsw_sql, "Created HNSW index (m=16, ef_construction=100)")

        # GIN index for full-text search on generated tsvector column
        execute_sql(
            client,
            "CREATE INDEX idx_products_search_vector ON products USING gin(search_vector)",
            "Created GIN index on search_vector"
        )

        # GIN indexes for JSONB pre-filtering
        # Requirement 5.2: JSONB capabilities for querying specifications and compatibility
        execute_sql(
            client,
            "CREATE INDEX idx_products_specs ON products USING gin(specifications jsonb_path_ops)",
            "Created GIN index on specifications (jsonb_path_ops)"
        )
        execute_sql(
            client,
            "CREATE INDEX idx_products_compat ON products USING gin(compatibility jsonb_path_ops)",
            "Created GIN index on compatibility (jsonb_path_ops)"
        )

        # B-tree indexes for category, brand, and price filtering
        execute_sql(
            client,
            "CREATE INDEX idx_products_category ON products(category)",
            "Created B-tree index on category"
        )
        execute_sql(
            client,
            "CREATE INDEX idx_products_brand ON products(brand)",
            "Created B-tree index on brand"
        )
        execute_sql(
            client,
            "CREATE INDEX idx_products_price ON products(price)",
            "Created B-tree index on price"
        )

        # Indexes for orders and order_items
        execute_sql(
            client,
            "CREATE INDEX idx_orders_customer ON orders(customer_id)",
            "Created index on orders(customer_id)"
        )
        execute_sql(
            client,
            "CREATE INDEX idx_orders_status ON orders(status)",
            "Created index on orders(status)"
        )
        execute_sql(
            client,
            "CREATE INDEX idx_orders_created ON orders(created_at DESC)",
            "Created index on orders(created_at)"
        )
        execute_sql(
            client,
            "CREATE INDEX idx_order_items_order ON order_items(order_id)",
            "Created index on order_items(order_id)"
        )

        # --- Create semantic search function (legacy, kept for Phase 1/2 compatibility) ---
        console.print("\n[yellow]Creating semantic_product_search function...[/yellow]")
        search_function_sql = """
        CREATE OR REPLACE FUNCTION semantic_product_search(
            query_embedding vector(1024),
            result_limit integer DEFAULT 5
        ) RETURNS TABLE (
            product_id varchar,
            name varchar,
            brand varchar,
            price decimal,
            description text,
            image_url varchar,
            category varchar,
            similarity float
        ) AS $$
        BEGIN
            RETURN QUERY
            SELECT
                p.product_id,
                p.name,
                p.brand,
                p.price,
                p.description,
                p.image_url,
                p.category,
                1 - (p.embedding <=> query_embedding) as similarity
            FROM products p
            WHERE p.embedding IS NOT NULL
            ORDER BY p.embedding <=> query_embedding
            LIMIT result_limit;
        END;
        $$ LANGUAGE plpgsql
        """
        execute_sql(client, search_function_sql, "Created semantic_product_search function")

        # --- Add table comments ---
        console.print("\n[yellow]Adding documentation comments...[/yellow]")
        execute_sql(
            client,
            "COMMENT ON TABLE products IS 'Product catalog with Cohere Embed v4 vector embeddings, JSONB specs/compatibility, and generated tsvector for hybrid search'",
            "Added products table comment"
        )
        execute_sql(
            client,
            "COMMENT ON COLUMN products.embedding IS 'Vector embedding for semantic/visual product search (1024-dim Cohere Embed v4)'",
            "Added embedding column comment"
        )
        execute_sql(
            client,
            "COMMENT ON COLUMN products.search_vector IS 'Auto-generated tsvector from name, description, and brand for full-text search'",
            "Added search_vector column comment"
        )
        execute_sql(
            client,
            "COMMENT ON COLUMN products.specifications IS 'Technical specifications as JSONB (connectivity, battery, audio, etc.)'",
            "Added specifications column comment"
        )
        execute_sql(
            client,
            "COMMENT ON COLUMN products.compatibility IS 'Ecosystem compatibility as JSONB (works_with, requires, pairs_with)'",
            "Added compatibility column comment"
        )
        execute_sql(
            client,
            "COMMENT ON COLUMN products.available_variants IS 'Product variants as JSONB (colors, sizes, configs) - replaces available_sizes'",
            "Added available_variants column comment"
        )

        # --- Create memory schema tables (Phase 4 - Agentic Memory and Personalization) ---
        # Requirement 3.1: Memory schema (conversations, preferences, interaction_embeddings)
        # Requirement 5.1: pgvector HNSW indexes for memory tables
        # Requirement 5.2: JSONB capabilities for agent memory
        console.print("\n[yellow]Creating memory schema tables (Phase 4)...[/yellow]")

        # Drop existing memory tables for clean reinstall
        memory_drop_statements = [
            ("DROP TABLE IF EXISTS interaction_embeddings CASCADE", "Dropped interaction_embeddings"),
            ("DROP TABLE IF EXISTS conversation_messages CASCADE", "Dropped conversation_messages"),
            ("DROP TABLE IF EXISTS customer_preferences CASCADE", "Dropped customer_preferences"),
            ("DROP TABLE IF EXISTS conversations CASCADE", "Dropped conversations"),
        ]
        for sql, desc in memory_drop_statements:
            execute_sql(client, sql, desc)

        # Create conversations table - stores high-level conversation metadata
        conversations_sql = """
        CREATE TABLE conversations (
            conversation_id VARCHAR(50) PRIMARY KEY,
            customer_id VARCHAR(50) NOT NULL,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            message_count INTEGER DEFAULT 0,
            summary TEXT
        )
        """
        execute_sql(client, conversations_sql, "Created conversations table")

        # Create conversation_messages table - individual messages with embeddings for semantic retrieval
        conversation_messages_sql = """
        CREATE TABLE conversation_messages (
            message_id VARCHAR(50) PRIMARY KEY,
            conversation_id VARCHAR(50) REFERENCES conversations(conversation_id),
            role VARCHAR(20) NOT NULL,
            content TEXT NOT NULL,
            embedding vector(1024),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        execute_sql(client, conversation_messages_sql, "Created conversation_messages table")

        # Create customer_preferences table - preference signals extracted by Memory Agent
        customer_preferences_sql = """
        CREATE TABLE customer_preferences (
            preference_id VARCHAR(50) PRIMARY KEY,
            customer_id VARCHAR(50) NOT NULL,
            preference_type VARCHAR(50) NOT NULL,
            preference_key VARCHAR(100) NOT NULL,
            confidence FLOAT DEFAULT 0.5,
            signal_count INTEGER DEFAULT 1,
            first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(customer_id, preference_type, preference_key)
        )
        """
        execute_sql(client, customer_preferences_sql, "Created customer_preferences table")

        # Create interaction_embeddings table - embeddings of full interactions for semantic memory
        interaction_embeddings_sql = """
        CREATE TABLE interaction_embeddings (
            interaction_id VARCHAR(50) PRIMARY KEY,
            customer_id VARCHAR(50) NOT NULL,
            conversation_id VARCHAR(50) REFERENCES conversations(conversation_id),
            query_text TEXT NOT NULL,
            response_summary TEXT,
            products_shown JSONB,
            embedding vector(1024),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        execute_sql(client, interaction_embeddings_sql, "Created interaction_embeddings table")

        # Create B-tree indexes for memory retrieval by customer and time
        console.print("[yellow]Creating memory B-tree indexes...[/yellow]")
        memory_btree_indexes = [
            ("CREATE INDEX idx_conversations_customer ON conversations(customer_id, last_message_at DESC)",
             "Created index on conversations(customer_id, last_message_at)"),
            ("CREATE INDEX idx_messages_conversation ON conversation_messages(conversation_id, created_at)",
             "Created index on conversation_messages(conversation_id, created_at)"),
            ("CREATE INDEX idx_preferences_customer ON customer_preferences(customer_id, preference_type)",
             "Created index on customer_preferences(customer_id, preference_type)"),
            ("CREATE INDEX idx_preferences_confidence ON customer_preferences(customer_id, confidence DESC)",
             "Created index on customer_preferences(customer_id, confidence)"),
            ("CREATE INDEX idx_interactions_customer ON interaction_embeddings(customer_id, created_at DESC)",
             "Created index on interaction_embeddings(customer_id, created_at)"),
        ]
        for sql, desc in memory_btree_indexes:
            execute_sql(client, sql, desc)

        # Create HNSW indexes for vector similarity search on memory embeddings
        console.print("[yellow]Creating memory HNSW indexes...[/yellow]")
        memory_hnsw_indexes = [
            ("""CREATE INDEX idx_messages_embedding ON conversation_messages
                USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)""",
             "Created HNSW index on conversation_messages embeddings"),
            ("""CREATE INDEX idx_interactions_embedding ON interaction_embeddings
                USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)""",
             "Created HNSW index on interaction_embeddings embeddings"),
        ]
        for sql, desc in memory_hnsw_indexes:
            execute_sql(client, sql, desc)

        # Add memory table comments
        console.print("[yellow]Adding memory table comments...[/yellow]")
        execute_sql(
            client,
            "COMMENT ON TABLE conversations IS 'Conversation history metadata for Phase 4 agentic memory'",
            "Added conversations table comment"
        )
        execute_sql(
            client,
            "COMMENT ON TABLE conversation_messages IS 'Individual messages with vector embeddings for semantic retrieval'",
            "Added conversation_messages table comment"
        )
        execute_sql(
            client,
            "COMMENT ON TABLE customer_preferences IS 'Customer preference signals extracted by Memory Agent (brand affinity, price sensitivity, etc.)'",
            "Added customer_preferences table comment"
        )
        execute_sql(
            client,
            "COMMENT ON TABLE interaction_embeddings IS 'Full interaction embeddings for semantic memory retrieval of past conversations'",
            "Added interaction_embeddings table comment"
        )

        # --- Create observability tables ---
        # Requirement 8.1: Token usage tracking (input/output tokens per agent invocation)
        # Requirement 8.2: Latency waterfall tracking (total_latency_ms, nested parent/child traces)
        # Requirement 8.4: Cost estimation per interaction (estimated_cost_usd)
        console.print("\n[yellow]Creating observability tables...[/yellow]")

        # Drop existing observability tables for clean reinstall
        execute_sql(client, "DROP TABLE IF EXISTS agent_traces CASCADE", "Dropped agent_traces")

        # Create agent_traces table - stores execution traces for each agent invocation
        agent_traces_sql = """
        CREATE TABLE agent_traces (
            trace_id VARCHAR(50) PRIMARY KEY,
            parent_trace_id VARCHAR(50) REFERENCES agent_traces(trace_id),
            conversation_id VARCHAR(50),
            agent_name VARCHAR(100) NOT NULL,
            phase INTEGER NOT NULL,
            input_tokens INTEGER DEFAULT 0,
            output_tokens INTEGER DEFAULT 0,
            embedding_calls INTEGER DEFAULT 0,
            db_queries INTEGER DEFAULT 0,
            total_latency_ms INTEGER,
            estimated_cost_usd DECIMAL(10, 6),
            status VARCHAR(20) DEFAULT 'success',
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        execute_sql(client, agent_traces_sql, "Created agent_traces table")

        # Create indexes for observability queries
        console.print("[yellow]Creating observability indexes...[/yellow]")
        execute_sql(
            client,
            "CREATE INDEX idx_traces_conversation ON agent_traces(conversation_id, created_at)",
            "Created index on agent_traces(conversation_id, created_at)"
        )
        execute_sql(
            client,
            "CREATE INDEX idx_traces_phase ON agent_traces(phase, created_at DESC)",
            "Created index on agent_traces(phase, created_at DESC)"
        )

        # Add observability table comments
        execute_sql(
            client,
            "COMMENT ON TABLE agent_traces IS 'Agent execution traces for observability: token usage, latency, and cost tracking'",
            "Added agent_traces table comment"
        )
        execute_sql(
            client,
            "COMMENT ON COLUMN agent_traces.parent_trace_id IS 'References parent trace for nested multi-agent delegation tracking'",
            "Added parent_trace_id column comment"
        )
        execute_sql(
            client,
            "COMMENT ON COLUMN agent_traces.estimated_cost_usd IS 'Estimated cost based on Bedrock pricing for Claude + Cohere Embed v4'",
            "Added estimated_cost_usd column comment"
        )

        # --- Verify installation ---
        console.print("\n[yellow]Verifying installation...[/yellow]")

        # Check tables
        tables_result = execute_sql(client, """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('products', 'customers', 'orders', 'order_items',
                               'conversations', 'conversation_messages', 'customer_preferences',
                               'interaction_embeddings', 'agent_traces')
            ORDER BY table_name
        """)
        tables = [r[0]['stringValue'] for r in tables_result.get('records', [])]

        # Check pgvector version
        vector_result = execute_sql(client, "SELECT extversion FROM pg_extension WHERE extname = 'vector'")
        vector_version = vector_result.get('records', [[]])[0][0].get('stringValue', 'unknown') if vector_result.get('records') else 'unknown'

        # Check indexes on products table
        indexes_result = execute_sql(client, """
            SELECT indexname
            FROM pg_indexes
            WHERE tablename = 'products'
            ORDER BY indexname
        """)
        product_indexes = [r[0]['stringValue'] for r in indexes_result.get('records', [])]

        # Display summary
        console.print("\n[bold green]🎉 Database Initialized Successfully![/bold green]\n")

        table = Table(title="Meridian 2026 Database Summary")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")

        table.add_row("Tables Created", ", ".join(tables) if tables else "products, customers, orders, order_items, conversations, conversation_messages, customer_preferences, interaction_embeddings, agent_traces")
        table.add_row("pgvector Extension", vector_version)
        table.add_row("Embedding Dimension", "1024 (Cohere Embed v4)")
        table.add_row("HNSW Index", "✅ m=16, ef_construction=100")
        table.add_row("GIN Indexes", "✅ search_vector, specifications, compatibility")
        table.add_row("B-tree Indexes", "✅ category, brand, price")
        table.add_row("Generated Column", "✅ search_vector (tsvector)")
        table.add_row("JSONB Fields", "✅ available_variants, inventory, specifications, compatibility, products_shown")
        table.add_row("Memory Schema", "✅ conversations, messages, preferences, interaction_embeddings")
        table.add_row("Memory HNSW Indexes", "✅ messages embedding, interactions embedding")
        table.add_row("Observability", "✅ agent_traces with conversation_id and phase indexes")
        table.add_row("semantic_product_search", "✅ Created (legacy)")
        table.add_row("Product Indexes", ", ".join(product_indexes) if product_indexes else "See above")

        console.print(table)

        console.print("\n[green]✅ Database schema ready for Meridian 2026![/green]")
        console.print("[yellow]Next step: Run seed_data.py to populate 36 products with Cohere Embed v4 embeddings[/yellow]")

    except Exception as e:
        console.print(f"[bold red]❌ Error: {e}[/bold red]")
        raise


if __name__ == "__main__":
    initialize_database()
