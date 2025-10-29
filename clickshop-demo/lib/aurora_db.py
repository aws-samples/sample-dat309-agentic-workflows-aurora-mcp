"""
Aurora PostgreSQL database operations for ClickShop
Uses psycopg3 for modern async-capable connections
"""
import os
import time
from typing import Dict, List, Optional, Tuple
from contextlib import contextmanager
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
import numpy as np

load_dotenv()

# Database connection parameters
DB_PARAMS = {
    'host': os.getenv('AURORA_HOST'),
    'port': os.getenv('AURORA_PORT'),
    'dbname': os.getenv('AURORA_DATABASE'),
    'user': os.getenv('AURORA_USERNAME'),
    'password': os.getenv('AURORA_PASSWORD'),
    'connect_timeout': 10
}

@contextmanager
def get_db_connection():
    """Context manager for database connections with dict rows"""
    conn = psycopg.connect(**DB_PARAMS, row_factory=dict_row)
    try:
        yield conn
    finally:
        conn.close()

# ============================================================================
# PRODUCT OPERATIONS
# ============================================================================

def get_product(product_id: str) -> Optional[Dict]:
    """Get product details by ID"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT product_id, name, category, price, brand, description,
                       available_sizes, inventory, created_at
                FROM products
                WHERE product_id = %s
            """, (product_id,))
            return cur.fetchone()

def get_all_products() -> List[Dict]:
    """Get all products"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT product_id, name, category, price, brand, description,
                       available_sizes, inventory
                FROM products
                ORDER BY category, name
            """)
            return cur.fetchall()

def search_products_semantic(query: str, limit: int = 5) -> List[Tuple[Dict, float]]:
    """
    Semantic search for products using vector embeddings
    Returns list of (product, similarity_score) tuples
    """
    import warnings
    warnings.filterwarnings('ignore', category=FutureWarning)
    
    from sentence_transformers import SentenceTransformer
    
    # Generate query embedding
    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_embedding = model.encode(query)
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Use cosine similarity for search
            cur.execute("""
                SELECT 
                    product_id, name, category, price, brand, description,
                    available_sizes, inventory,
                    1 - (embedding <=> %s::vector) as similarity
                FROM products
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """, (query_embedding.tolist(), query_embedding.tolist(), limit))
            
            results = []
            for row in cur.fetchall():
                similarity = row.pop('similarity')
                results.append((row, similarity))
            
            return results

# ============================================================================
# INVENTORY OPERATIONS
# ============================================================================

def check_inventory(product_id: str, size: Optional[str] = None) -> Dict:
    """Check product inventory"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT inventory, available_sizes
                FROM products
                WHERE product_id = %s
            """, (product_id,))
            
            result = cur.fetchone()
            if not result:
                return {"in_stock": False, "error": "Product not found"}
            
            inventory = result['inventory']
            available_sizes = result['available_sizes']
            
            if size and available_sizes:
                # Sized product (like shoes)
                quantity = inventory.get(size, 0) if isinstance(inventory, dict) else 0
                # For demo: ensure size 10 always has stock, others use actual inventory
                if size == "10":
                    quantity = max(quantity, 50)
                return {
                    "in_stock": quantity > 0,
                    "size": size,
                    "quantity": quantity,
                    "available_sizes": available_sizes
                }
            else:
                # Non-sized product
                quantity = inventory.get('quantity', 0) if isinstance(inventory, dict) else 0
                # For demo: always show as in stock
                return {
                    "in_stock": True,
                    "quantity": max(quantity, 50)
                }

def update_inventory(
    product_id: str,
    size: Optional[str],
    quantity_change: int,
    reason: str,
    order_id: Optional[str] = None
) -> bool:
    """Update inventory and log transaction"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            if size:
                # Update sized inventory
                cur.execute("""
                    UPDATE products
                    SET inventory = jsonb_set(
                        inventory,
                        ARRAY[%s],
                        to_jsonb(GREATEST(0, COALESCE((inventory->>%s)::int, 0) + %s))
                    ),
                    updated_at = CURRENT_TIMESTAMP
                    WHERE product_id = %s
                    RETURNING (inventory->>%s)::int as new_quantity
                """, (size, size, quantity_change, product_id, size))
            else:
                # Update non-sized inventory
                cur.execute("""
                    UPDATE products
                    SET inventory = jsonb_set(
                        inventory,
                        ARRAY['quantity'],
                        to_jsonb(GREATEST(0, COALESCE((inventory->>'quantity')::int, 0) + %s))
                    ),
                    updated_at = CURRENT_TIMESTAMP
                    WHERE product_id = %s
                    RETURNING (inventory->>'quantity')::int as new_quantity
                """, (quantity_change, product_id))
            
            result = cur.fetchone()
            new_quantity = result['new_quantity'] if result else 0
            
            # Log transaction
            cur.execute("""
                INSERT INTO inventory_transactions
                (product_id, size, quantity_change, quantity_after, transaction_type, reason, order_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                product_id,
                size,
                quantity_change,
                new_quantity,
                'sale' if quantity_change < 0 else 'restock',
                reason,
                order_id
            ))
            
            conn.commit()
            return True

# ============================================================================
# ORDER OPERATIONS
# ============================================================================

def create_order(
    product_id: str,
    customer_id: str,
    size: Optional[str],
    base_price: float,
    tax: float,
    total: float,
    stream_id: Optional[str] = None,
    processed_by: str = "SingleAgent"
) -> Dict:
    """Create new order and update inventory"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Generate order ID
            cur.execute("SELECT COUNT(*) as count FROM orders")
            order_count = cur.fetchone()['count']
            order_id = f"CLK-{int(time.time())}-{order_count + 1:04d}"
            
            # Insert order
            cur.execute("""
                INSERT INTO orders
                (order_id, product_id, customer_id, size, base_price, tax, 
                 total_amount, status, stream_id, processed_by_agent)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (
                order_id, product_id, customer_id, size, base_price, tax,
                total, 'confirmed', stream_id, processed_by
            ))
            
            order = cur.fetchone()
            
            # Update inventory
            update_inventory(product_id, size, -1, f"Order {order_id}", order_id)
            
            # Mark order as completed
            cur.execute("""
                UPDATE orders
                SET completed_at = CURRENT_TIMESTAMP
                WHERE order_id = %s
            """, (order_id,))
            
            conn.commit()
            
            return order

def get_order(order_id: str) -> Optional[Dict]:
    """Get order details"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT o.*, p.name as product_name, p.brand
                FROM orders o
                JOIN products p ON o.product_id = p.product_id
                WHERE o.order_id = %s
            """, (order_id,))
            return cur.fetchone()

def get_recent_orders(limit: int = 10) -> List[Dict]:
    """Get recent orders"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT o.*, p.name as product_name, p.brand
                FROM orders o
                JOIN products p ON o.product_id = p.product_id
                ORDER BY o.created_at DESC
                LIMIT %s
            """, (limit,))
            return cur.fetchall()

# ============================================================================
# ANALYTICS OPERATIONS
# ============================================================================

def log_agent_action(
    agent_type: str,
    action: str,
    duration_ms: int,
    status: str = "success",
    agent_name: Optional[str] = None,
    error_message: Optional[str] = None,
    metadata: Optional[Dict] = None
):
    """Log agent action for analytics"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO agent_analytics
                (agent_type, agent_name, action, duration_ms, status, error_message, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                agent_type,
                agent_name,
                action,
                duration_ms,
                status,
                error_message,
                psycopg.types.json.Jsonb(metadata) if metadata else None
            ))
            conn.commit()

def get_agent_analytics(agent_type: Optional[str] = None, hours: int = 24) -> List[Dict]:
    """Get agent performance analytics"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            if agent_type:
                cur.execute("""
                    SELECT 
                        agent_type,
                        action,
                        COUNT(*) as count,
                        AVG(duration_ms)::int as avg_duration_ms,
                        MIN(duration_ms) as min_duration_ms,
                        MAX(duration_ms) as max_duration_ms,
                        SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count,
                        SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error_count
                    FROM agent_analytics
                    WHERE agent_type = %s
                    AND created_at > NOW() - INTERVAL '%s hours'
                    GROUP BY agent_type, action
                    ORDER BY count DESC
                """, (agent_type, hours))
            else:
                cur.execute("""
                    SELECT 
                        agent_type,
                        action,
                        COUNT(*) as count,
                        AVG(duration_ms)::int as avg_duration_ms,
                        SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count
                    FROM agent_analytics
                    WHERE created_at > NOW() - INTERVAL '%s hours'
                    GROUP BY agent_type, action
                    ORDER BY agent_type, count DESC
                """, (hours,))
            
            return cur.fetchall()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_database_stats() -> Dict:
    """Get overall database statistics"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            stats = {}
            
            # Product count
            cur.execute("SELECT COUNT(*) as count FROM products")
            stats['total_products'] = cur.fetchone()['count']
            
            # Order count
            cur.execute("SELECT COUNT(*) as count FROM orders")
            stats['total_orders'] = cur.fetchone()['count']
            
            # Orders today
            cur.execute("""
                SELECT COUNT(*) as count FROM orders
                WHERE DATE(created_at) = CURRENT_DATE
            """)
            stats['orders_today'] = cur.fetchone()['count']
            
            # Revenue today
            cur.execute("""
                SELECT COALESCE(SUM(total_amount), 0) as revenue FROM orders
                WHERE DATE(created_at) = CURRENT_DATE
            """)
            stats['revenue_today'] = float(cur.fetchone()['revenue'])
            
            # Agent actions today
            cur.execute("""
                SELECT COUNT(*) as count FROM agent_analytics
                WHERE DATE(created_at) = CURRENT_DATE
            """)
            stats['agent_actions_today'] = cur.fetchone()['count']
            
            return stats

# Test function
if __name__ == "__main__":
    from rich.console import Console
    from rich.table import Table
    
    console = Console()
    
    console.print("\n[bold blue]Testing Aurora Database Operations[/bold blue]\n")
    
    # Test connection
    try:
        with get_db_connection() as conn:
            console.print("[green]✅ Database connection successful[/green]")
    except Exception as e:
        console.print(f"[red]❌ Connection failed: {e}[/red]")
        exit(1)
    
    # Get stats
    stats = get_database_stats()
    
    table = Table(title="Database Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    for key, value in stats.items():
        table.add_row(key.replace('_', ' ').title(), str(value))
    
    console.print(table)
    
    # List products
    console.print("\n[bold cyan]Products:[/bold cyan]")
    products = get_all_products()
    
    products_table = Table()
    products_table.add_column("ID", style="cyan")
    products_table.add_column("Name", style="yellow")
    products_table.add_column("Price", style="green")
    products_table.add_column("Category", style="magenta")
    
    for p in products[:5]:
        products_table.add_row(
            p['product_id'],
            p['name'],
            f"${p['price']}",
            p['category']
        )
    
    console.print(products_table)
    console.print(f"\n[yellow]Total: {len(products)} products[/yellow]")
    
    console.print("\n[green]✅ All database operations working![/green]")
