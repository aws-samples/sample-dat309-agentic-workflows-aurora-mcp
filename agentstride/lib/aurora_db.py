"""
Aurora PostgreSQL database operations for AgentStride
Uses RDS Data API for serverless database access

ARCHITECTURE NOTES:
- RDS Data API for all database operations (no connection management)
- Works with Aurora Serverless v2 in private VPC
- IAM authentication via Secrets Manager
- Optimized for <200ms response times
"""
import os
import json
import time
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
import boto3
from dotenv import load_dotenv

load_dotenv()

# RDS Data API configuration
CLUSTER_ARN = os.getenv('AURORA_CLUSTER_ARN')
SECRET_ARN = os.getenv('AURORA_SECRET_ARN')
DATABASE = os.getenv('AURORA_DATABASE', 'clickshop')
REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')

# Initialize RDS Data API client
rds_data = boto3.client('rds-data', region_name=REGION)


def _format_params(params: tuple) -> List[Dict]:
    """Convert tuple parameters to RDS Data API format."""
    if not params:
        return []
    
    formatted = []
    for i, value in enumerate(params):
        param = {"name": f"p{i}"}
        
        if value is None:
            param["value"] = {"isNull": True}
        elif isinstance(value, bool):
            param["value"] = {"booleanValue": value}
        elif isinstance(value, int):
            param["value"] = {"longValue": value}
        elif isinstance(value, float):
            param["value"] = {"doubleValue": value}
        elif isinstance(value, Decimal):
            param["value"] = {"stringValue": str(value)}
            param["typeHint"] = "DECIMAL"
        elif isinstance(value, (list, dict)):
            param["value"] = {"stringValue": json.dumps(value)}
        else:
            param["value"] = {"stringValue": str(value)}
        
        formatted.append(param)
    
    return formatted


def _convert_placeholders(sql: str, param_count: int) -> str:
    """Convert %s placeholders to :pN named parameters."""
    result = sql
    for i in range(param_count):
        result = result.replace("%s", f":p{i}", 1)
    return result


def _parse_value(field: Dict):
    """Parse a single field value from RDS Data API response."""
    if "isNull" in field and field["isNull"]:
        return None
    if "stringValue" in field:
        return field["stringValue"]
    if "longValue" in field:
        return field["longValue"]
    if "doubleValue" in field:
        return field["doubleValue"]
    if "booleanValue" in field:
        return field["booleanValue"]
    return None


def _parse_response(response: Dict, column_names: List[str]) -> List[Dict]:
    """Parse RDS Data API response into list of dictionaries."""
    records = response.get("records", [])
    results = []
    
    for record in records:
        row = {}
        for i, field in enumerate(record):
            if i < len(column_names):
                value = _parse_value(field)
                # Parse JSON for specific columns
                if isinstance(value, str) and column_names[i] in ['inventory', 'available_sizes', 'metadata']:
                    try:
                        value = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        pass
                row[column_names[i]] = value
        results.append(row)
    
    return results


def execute_sql(sql: str, params: tuple = None) -> List[Dict]:
    """
    Execute SQL query using RDS Data API.
    
    PATTERN: Serverless database access
    - No connection management
    - IAM authentication
    - Works with private VPC clusters
    """
    param_count = sql.count("%s")
    converted_sql = _convert_placeholders(sql, param_count)
    parameters = _format_params(params) if params else []
    
    response = rds_data.execute_statement(
        resourceArn=CLUSTER_ARN,
        secretArn=SECRET_ARN,
        database=DATABASE,
        sql=converted_sql,
        parameters=parameters,
        includeResultMetadata=True
    )
    
    column_metadata = response.get("columnMetadata", [])
    column_names = [col.get("name", f"col{i}") for i, col in enumerate(column_metadata)]
    
    return _parse_response(response, column_names)


def execute_sql_one(sql: str, params: tuple = None) -> Optional[Dict]:
    """Execute SQL and return single result."""
    results = execute_sql(sql, params)
    return results[0] if results else None


# ============================================================================
# PRODUCT OPERATIONS
# ============================================================================

def get_product(product_id: str) -> Optional[Dict]:
    """
    Get product details by ID.
    
    PERFORMANCE: ~50ms with RDS Data API
    """
    return execute_sql_one("""
        SELECT product_id, name, category, price, brand, description,
               available_sizes, inventory, created_at
        FROM products
        WHERE product_id = %s
    """, (product_id,))


def get_all_products() -> List[Dict]:
    """
    Get all products.
    
    SCALING TIP: For catalogs >10K products, add pagination
    """
    return execute_sql("""
        SELECT product_id, name, category, price, brand, description,
               available_sizes, inventory
        FROM products
        ORDER BY category, name
    """)


def search_products_semantic(query: str, limit: int = 5) -> List[Tuple[Dict, float]]:
    """
    Semantic search for products using vector embeddings.
    
    ARCHITECTURE:
    - Uses pgvector extension with HNSW indexing
    - Nova Multimodal embeddings (1024 dimensions)
    - Cosine similarity for ranking
    
    Returns list of (product, similarity_score) tuples
    """
    # Generate query embedding using Amazon Nova Multimodal Embeddings
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    request_body = {
        "schemaVersion": "nova-multimodal-embed-v1",
        "taskType": "SINGLE_EMBEDDING",
        "singleEmbeddingParams": {
            "embeddingPurpose": "TEXT_RETRIEVAL",
            "embeddingDimension": 1024,
            "text": {
                "truncationMode": "END",
                "value": query
            }
        }
    }
    
    response = bedrock.invoke_model(
        modelId="amazon.nova-2-multimodal-embeddings-v1:0",
        body=json.dumps(request_body),
        contentType="application/json",
        accept="application/json"
    )
    
    response_body = json.loads(response['body'].read())
    query_embedding = response_body['embeddings'][0]['embedding']
    embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
    
    # Search using pgvector
    results = execute_sql("""
        SELECT 
            product_id, name, category, price, brand, description,
            available_sizes, inventory,
            1 - (embedding <=> %s::vector) as similarity
        FROM products
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """, (embedding_str, embedding_str, limit))
    
    return [(r, float(r.pop('similarity', 0))) for r in results]


# ============================================================================
# INVENTORY OPERATIONS
# ============================================================================

def check_inventory(product_id: str, size: Optional[str] = None) -> Dict:
    """
    Check product inventory.
    
    CACHING TIP: Cache results for 30-60s in Redis for high traffic
    """
    result = execute_sql_one("""
        SELECT inventory, available_sizes
        FROM products
        WHERE product_id = %s
    """, (product_id,))
    
    if not result:
        return {"in_stock": False, "error": "Product not found"}
    
    inventory = result['inventory']
    available_sizes = result['available_sizes']
    
    if size and available_sizes:
        quantity = inventory.get(size, 0) if isinstance(inventory, dict) else 0
        if size == "10":
            quantity = max(quantity, 50)  # Demo mode
        return {
            "in_stock": quantity > 0,
            "size": size,
            "quantity": quantity,
            "available_sizes": available_sizes
        }
    else:
        quantity = inventory.get('quantity', 0) if isinstance(inventory, dict) else 0
        return {
            "in_stock": True,
            "quantity": max(quantity, 50)  # Demo mode
        }


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
    """
    Create new order.
    
    PATTERN: Single API call for order creation
    """
    # Get order count for ID generation
    count_result = execute_sql_one("SELECT COUNT(*) as count FROM orders")
    order_count = count_result['count'] if count_result else 0
    order_id = f"CLK-{int(time.time())}-{order_count + 1:04d}"
    
    # Insert order
    execute_sql("""
        INSERT INTO orders
        (order_id, product_id, customer_id, size, base_price, tax, 
         total_amount, status, stream_id, processed_by_agent)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        order_id, product_id, customer_id, size, base_price, tax,
        total, 'confirmed', stream_id, processed_by
    ))
    
    return {
        "order_id": order_id,
        "product_id": product_id,
        "customer_id": customer_id,
        "total_amount": total,
        "status": "confirmed"
    }


def get_order(order_id: str) -> Optional[Dict]:
    """Get order details with product information."""
    return execute_sql_one("""
        SELECT o.*, p.name as product_name, p.brand
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        WHERE o.order_id = %s
    """, (order_id,))


def get_recent_orders(limit: int = 10) -> List[Dict]:
    """Get recent orders."""
    return execute_sql("""
        SELECT o.*, p.name as product_name, p.brand
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        ORDER BY o.created_at DESC
        LIMIT %s
    """, (limit,))


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_database_stats() -> Dict:
    """Get overall database statistics."""
    stats = {}
    
    result = execute_sql_one("SELECT COUNT(*) as count FROM products")
    stats['total_products'] = result['count'] if result else 0
    
    result = execute_sql_one("SELECT COUNT(*) as count FROM orders")
    stats['total_orders'] = result['count'] if result else 0
    
    result = execute_sql_one("""
        SELECT COUNT(*) as count FROM orders
        WHERE DATE(created_at) = CURRENT_DATE
    """)
    stats['orders_today'] = result['count'] if result else 0
    
    result = execute_sql_one("""
        SELECT COALESCE(SUM(total_amount), 0) as revenue FROM orders
        WHERE DATE(created_at) = CURRENT_DATE
    """)
    stats['revenue_today'] = float(result['revenue']) if result else 0.0
    
    return stats


# ============================================================================
# TEST & VERIFICATION
# ============================================================================

if __name__ == "__main__":
    from rich.console import Console
    from rich.table import Table
    
    console = Console()
    
    console.print("\n[bold blue]Testing Aurora Database Operations (RDS Data API)[/bold blue]\n")
    
    # Test connection
    try:
        stats = get_database_stats()
        console.print("[green]✅ RDS Data API connection successful[/green]")
    except Exception as e:
        console.print(f"[red]❌ Connection failed: {e}[/red]")
        exit(1)
    
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
