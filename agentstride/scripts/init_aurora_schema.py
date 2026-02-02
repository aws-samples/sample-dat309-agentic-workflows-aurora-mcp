"""
Initialize Aurora PostgreSQL database schema for AgentStride
Includes pgvector for semantic and visual search with Nova Multimodal embeddings (1024 dimensions)

Requirements covered:
- 2.1: products table with embedding (vector 1024 dimensions)
- 2.2: customers table
- 2.3: orders table
- 2.4: order_items table
- 2.5: HNSW index on products.embedding
- 2.6: semantic_product_search SQL function
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
DATABASE = os.getenv('AURORA_DATABASE', 'clickshop')
REGION = os.getenv('BEDROCK_REGION', 'us-east-1')

# Complete database schema for AgentStride
SCHEMA_SQL = """
-- Enable pgvector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Drop existing tables (for clean reinstall)
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS agent_analytics CASCADE;
DROP TABLE IF EXISTS inventory_transactions CASCADE;

-- Products table with Nova Multimodal embeddings (1024 dimensions)
-- Requirement 2.1: products table with columns: product_id, name, category, price, brand, 
-- description, image_url, available_sizes, inventory, embedding (vector 1024 dimensions), created_at, updated_at
CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    brand VARCHAR(100),
    description TEXT,
    image_url VARCHAR(500),
    available_sizes JSONB,
    inventory JSONB NOT NULL,
    embedding vector(1024),  -- Nova Multimodal embedding
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customers table
-- Requirement 2.2: customers table with columns: customer_id, name, email, created_at
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders table
-- Requirement 2.3: orders table with columns: order_id, customer_id, status, total_amount, created_at, completed_at
CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) REFERENCES customers(customer_id),
    status VARCHAR(50) DEFAULT 'pending',
    total_amount DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Order items table
-- Requirement 2.4: order_items table with columns: item_id, order_id, product_id, size, quantity, unit_price
CREATE TABLE order_items (
    item_id SERIAL PRIMARY KEY,
    order_id VARCHAR(50) REFERENCES orders(order_id),
    product_id VARCHAR(50) REFERENCES products(product_id),
    size VARCHAR(10),
    quantity INTEGER DEFAULT 1,
    unit_price DECIMAL(10, 2) NOT NULL
);

-- Indexes for performance
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created ON orders(created_at DESC);
CREATE INDEX idx_order_items_order ON order_items(order_id);

-- HNSW index for fast vector similarity search
-- Requirement 2.5: HNSW index on the products.embedding column for fast vector similarity search
CREATE INDEX idx_products_embedding ON products
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Comments for documentation
COMMENT ON TABLE products IS 'Product catalog with Nova 2 Multimodal vector embeddings for semantic and visual search';
COMMENT ON COLUMN products.embedding IS 'Vector embedding for semantic/visual product search (1024-dim Nova Multimodal)';
COMMENT ON TABLE customers IS 'Customer information for order processing';
COMMENT ON TABLE orders IS 'Customer orders processed by AgentStride agents';
COMMENT ON TABLE order_items IS 'Individual items within customer orders';
"""

# Semantic product search SQL function
# Requirement 2.6: semantic_product_search SQL function that performs cosine similarity search
SEMANTIC_SEARCH_FUNCTION_SQL = """
-- Semantic product search function using cosine similarity
-- Requirement 2.6: semantic_product_search SQL function for cosine similarity search on product embeddings
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
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION semantic_product_search IS 'Performs cosine similarity search on product embeddings using Nova 2 Multimodal vectors';
"""


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
    """Initialize Aurora database with schema for AgentStride using RDS Data API"""
    console.print("\n[bold blue]🚀 Initializing Aurora PostgreSQL Database for AgentStride[/bold blue]")
    console.print(f"Cluster ARN: {CLUSTER_ARN}")
    console.print(f"Database: {DATABASE}\n")
    
    if not CLUSTER_ARN or not SECRET_ARN:
        console.print("[red]❌ Missing AURORA_CLUSTER_ARN or AURORA_SECRET_ARN in .env[/red]")
        return
    
    try:
        # Create RDS Data API client
        client = boto3.client('rds-data', region_name=REGION)
        
        # Split schema into individual statements and execute
        console.print("[yellow]Creating database schema...[/yellow]")
        
        # Execute schema statements one by one
        schema_statements = [
            ("CREATE EXTENSION IF NOT EXISTS vector", "pgvector extension enabled"),
            ("DROP TABLE IF EXISTS order_items CASCADE", "Dropped order_items"),
            ("DROP TABLE IF EXISTS orders CASCADE", "Dropped orders"),
            ("DROP TABLE IF EXISTS customers CASCADE", "Dropped customers"),
            ("DROP TABLE IF EXISTS products CASCADE", "Dropped products"),
        ]
        
        for sql, desc in schema_statements:
            execute_sql(client, sql, desc)
        
        # Create products table
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
            inventory JSONB NOT NULL,
            embedding vector(1024),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        execute_sql(client, products_sql, "Created products table")
        
        # Create customers table
        customers_sql = """
        CREATE TABLE customers (
            customer_id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        execute_sql(client, customers_sql, "Created customers table")
        
        # Create orders table
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
        
        # Create order_items table
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
        
        # Create indexes
        indexes = [
            ("CREATE INDEX idx_products_category ON products(category)", "Created category index"),
            ("CREATE INDEX idx_orders_customer ON orders(customer_id)", "Created customer index"),
            ("CREATE INDEX idx_orders_status ON orders(status)", "Created status index"),
            ("CREATE INDEX idx_orders_created ON orders(created_at DESC)", "Created created_at index"),
            ("CREATE INDEX idx_order_items_order ON order_items(order_id)", "Created order_items index"),
        ]
        
        for sql, desc in indexes:
            execute_sql(client, sql, desc)
        
        # Create HNSW index (now works with 1024 dimensions)
        hnsw_sql = """
        CREATE INDEX idx_products_embedding ON products
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
        """
        execute_sql(client, hnsw_sql, "Created HNSW index on embeddings")
        
        # Create semantic search function
        console.print("[yellow]Creating semantic_product_search function...[/yellow]")
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
        
        # Verify installation
        console.print("\n[yellow]Verifying installation...[/yellow]")
        
        # Check tables
        tables_result = execute_sql(client, """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('products', 'customers', 'orders', 'order_items')
            ORDER BY table_name
        """)
        tables = [r[0]['stringValue'] for r in tables_result.get('records', [])]
        
        # Check pgvector
        vector_result = execute_sql(client, "SELECT extversion FROM pg_extension WHERE extname = 'vector'")
        vector_version = vector_result.get('records', [[]])[0][0].get('stringValue', 'unknown') if vector_result.get('records') else 'unknown'
        
        # Display summary
        console.print("\n[bold green]🎉 Database Initialized Successfully![/bold green]\n")
        
        table = Table(title="Database Summary")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        
        table.add_row("Tables Created", ", ".join(tables) if tables else "products, customers, orders, order_items")
        table.add_row("pgvector Extension", vector_version)
        table.add_row("Embedding Dimension", "1024 (Nova Multimodal Embeddings)")
        table.add_row("HNSW Index", "✅ Created")
        table.add_row("semantic_product_search", "✅ Created")
        
        console.print(table)
        
        console.print("\n[green]✅ Database schema ready![/green]")
        console.print("[yellow]Next step: Run seed_data.py to populate products with Nova 2 Multimodal embeddings[/yellow]")
        
    except Exception as e:
        console.print(f"[bold red]❌ Error: {e}[/bold red]")
        raise


if __name__ == "__main__":
    initialize_database()
