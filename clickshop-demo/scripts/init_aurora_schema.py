"""
Initialize Aurora PostgreSQL database schema for ClickShop
Includes pgvector for semantic search capabilities
"""
import os
import psycopg
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv()
console = Console()

# Complete database schema
SCHEMA_SQL = """
-- Enable pgvector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Drop existing tables (for clean reinstall)
DROP TABLE IF EXISTS agent_analytics CASCADE;
DROP TABLE IF EXISTS inventory_transactions CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;

-- Products table with vector embeddings
CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    price DECIMAL(10, 2) NOT NULL,
    brand VARCHAR(100),
    description TEXT,
    available_sizes JSONB,
    inventory JSONB,
    
    -- Vector embedding for semantic search (384 dimensions for all-MiniLM-L6-v2)
    embedding vector(384),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders table
CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    product_id VARCHAR(50) REFERENCES products(product_id),
    customer_id VARCHAR(50) NOT NULL,
    size VARCHAR(10),
    quantity INTEGER DEFAULT 1,
    base_price DECIMAL(10, 2),
    tax DECIMAL(10, 2),
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    stream_id VARCHAR(100),
    
    -- Agent that processed the order
    processed_by_agent VARCHAR(50),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Inventory transactions for audit trail
CREATE TABLE inventory_transactions (
    transaction_id SERIAL PRIMARY KEY,
    product_id VARCHAR(50) REFERENCES products(product_id),
    size VARCHAR(10),
    quantity_change INTEGER NOT NULL,
    quantity_after INTEGER,
    transaction_type VARCHAR(50) NOT NULL,
    reason TEXT,
    order_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agent analytics for performance tracking
CREATE TABLE agent_analytics (
    analytics_id SERIAL PRIMARY KEY,
    agent_type VARCHAR(50) NOT NULL,
    agent_name VARCHAR(100),
    action VARCHAR(100) NOT NULL,
    duration_ms INTEGER,
    status VARCHAR(50) DEFAULT 'success',
    error_message TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created ON orders(created_at DESC);
CREATE INDEX idx_orders_product ON orders(product_id);

CREATE INDEX idx_inventory_product ON inventory_transactions(product_id);
CREATE INDEX idx_inventory_created ON inventory_transactions(created_at DESC);

CREATE INDEX idx_analytics_agent_type ON agent_analytics(agent_type);
CREATE INDEX idx_analytics_created ON agent_analytics(created_at DESC);
CREATE INDEX idx_analytics_status ON agent_analytics(status);

-- Vector similarity index for fast semantic search (HNSW with cosine distance)
CREATE INDEX idx_products_embedding ON products 
USING hnsw (embedding vector_cosine_ops);

-- Comments for documentation
COMMENT ON TABLE products IS 'Product catalog with vector embeddings for semantic search';
COMMENT ON COLUMN products.embedding IS 'Vector embedding for semantic product search (384-dim)';
COMMENT ON TABLE orders IS 'Customer orders processed by ClickShop agents';
COMMENT ON TABLE inventory_transactions IS 'Audit trail for all inventory changes';
COMMENT ON TABLE agent_analytics IS 'Performance metrics for agent system';
"""

# Sample products with descriptions for embedding
SAMPLE_PRODUCTS = [
    {
        'product_id': 'shoe_001',
        'name': 'Nike Air Zoom Pegasus',
        'category': 'running_shoes',
        'price': 120.00,
        'brand': 'Nike',
        'description': 'Responsive cushioning running shoes perfect for daily training and long distance runs. Lightweight mesh upper with excellent breathability.',
        'available_sizes': '["8", "9", "10", "11", "12"]',
        'inventory': '{"8": 3, "9": 5, "10": 5, "11": 2, "12": 1}'
    },
    {
        'product_id': 'band_001',
        'name': 'Resistance Band Set',
        'category': 'fitness',
        'price': 29.99,
        'brand': 'FitPro',
        'description': 'Complete 5-piece resistance band set for full body workouts. Multiple resistance levels from light to heavy. Perfect for home gym.',
        'available_sizes': None,
        'inventory': '{"quantity": 50}'
    },
    {
        'product_id': 'mat_001',
        'name': 'Premium Yoga Mat',
        'category': 'fitness',
        'price': 49.99,
        'brand': 'ZenFlow',
        'description': 'Eco-friendly non-slip yoga mat with excellent cushioning. 6mm thick for comfort during floor exercises and yoga poses.',
        'available_sizes': None,
        'inventory': '{"quantity": 25}'
    },
    {
        'product_id': 'bottle_001',
        'name': 'Insulated Water Bottle',
        'category': 'accessories',
        'price': 34.99,
        'brand': 'HydroMax',
        'description': 'Stainless steel insulated water bottle keeps drinks cold for 24 hours. Perfect companion for workouts and outdoor activities.',
        'available_sizes': None,
        'inventory': '{"quantity": 40}'
    },
    {
        'product_id': 'shoe_002',
        'name': 'Trail Running Shoes',
        'category': 'running_shoes',
        'price': 135.00,
        'brand': 'Salomon',
        'description': 'Rugged trail running shoes with aggressive grip and waterproof protection. Built for mountain terrain and muddy conditions.',
        'available_sizes': '["8", "9", "10", "11", "12"]',
        'inventory': '{"8": 2, "9": 3, "10": 4, "11": 3, "12": 2}'
    },
    {
        'product_id': 'shorts_001',
        'name': 'Athletic Shorts',
        'category': 'apparel',
        'price': 39.99,
        'brand': 'Nike',
        'description': 'Lightweight athletic shorts with moisture-wicking fabric. Built-in liner and zippered pocket for valuables during runs.',
        'available_sizes': '["S", "M", "L", "XL"]',
        'inventory': '{"S": 10, "M": 15, "L": 12, "XL": 8}'
    }
]

def initialize_database():
    """Initialize Aurora database with schema and sample data"""
    console.print("\n[bold blue]🚀 Initializing Aurora PostgreSQL Database[/bold blue]")
    console.print(f"Host: {os.getenv('AURORA_HOST')}")
    console.print(f"Database: {os.getenv('AURORA_DATABASE')}\n")
    
    try:
        # Connect to Aurora
        conn = psycopg.connect(
            host=os.getenv('AURORA_HOST'),
            port=os.getenv('AURORA_PORT'),
            dbname=os.getenv('AURORA_DATABASE'),
            user=os.getenv('AURORA_USERNAME'),
            password=os.getenv('AURORA_PASSWORD')
        )
        
        with conn.cursor() as cur:
            # Create schema
            console.print("[yellow]Creating database schema...[/yellow]")
            cur.execute(SCHEMA_SQL)
            conn.commit()
            console.print("[green]✅ Schema created successfully[/green]")
            
            # Insert products (without embeddings for now)
            console.print("\n[yellow]Inserting sample products...[/yellow]")
            for product in SAMPLE_PRODUCTS:
                cur.execute("""
                    INSERT INTO products 
                    (product_id, name, category, price, brand, description, available_sizes, inventory)
                    VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb)
                """, (
                    product['product_id'],
                    product['name'],
                    product['category'],
                    product['price'],
                    product['brand'],
                    product['description'],
                    product['available_sizes'],
                    product['inventory']
                ))
            
            conn.commit()
            console.print(f"[green]✅ Inserted {len(SAMPLE_PRODUCTS)} products[/green]")
            
            # Verify installation
            cur.execute("SELECT COUNT(*) FROM products;")
            product_count = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM orders;")
            order_count = cur.fetchone()[0]
            
            # Check pgvector
            cur.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector';")
            vector_version = cur.fetchone()
            
            # Display summary
            console.print("\n[bold green]🎉 Database Initialized Successfully![/bold green]\n")
            
            table = Table(title="Database Summary")
            table.add_column("Item", style="cyan")
            table.add_column("Status", style="green")
            
            table.add_row("Products", str(product_count))
            table.add_row("Orders", str(order_count))
            table.add_row("pgvector Extension", vector_version[0] if vector_version else "Not installed")
            table.add_row("Embedding Dimension", "384 (all-MiniLM-L6-v2)")
            
            console.print(table)
            
            # Show sample products
            console.print("\n[bold cyan]Sample Products:[/bold cyan]")
            cur.execute("""
                SELECT product_id, name, category, price, brand
                FROM products
                ORDER BY category, name
            """)
            
            products_table = Table()
            products_table.add_column("ID", style="cyan")
            products_table.add_column("Name", style="yellow")
            products_table.add_column("Category", style="magenta")
            products_table.add_column("Price", style="green")
            products_table.add_column("Brand", style="blue")
            
            for row in cur.fetchall():
                products_table.add_row(
                    row[0],
                    row[1],
                    row[2],
                    f"${row[3]}",
                    row[4]
                )
            
            console.print(products_table)
            
        conn.close()
        
        console.print("\n[green]✅ Ready to run demos![/green]")
        console.print("[yellow]Next step: Generate embeddings for semantic search (Month 3)[/yellow]")
        
    except Exception as e:
        console.print(f"[bold red]❌ Error: {e}[/bold red]")
        raise

if __name__ == "__main__":
    initialize_database()
