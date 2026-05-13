"""
Seed data script for Meridian
Populates Aurora PostgreSQL with 30 travel packages across 6 categories
Generates 1024-dimensional embeddings using Cohere Embed v4

Requirements covered:
- 2.7: Populate 30 travel packages across 6 categories
- 2.8: Generate 1024-dimensional embeddings using Cohere Embed v4
"""
import os
import json
import boto3
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import track
from rich.table import Table

load_dotenv()
console = Console()

# Cohere Embed v4 Configuration
EMBEDDING_MODEL_ID = os.getenv("EMBEDDING_MODEL", "global.cohere.embed-v4")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1024"))
BEDROCK_REGION = os.getenv('BEDROCK_REGION', 'us-west-2')
AURORA_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')

# RDS Data API Configuration
CLUSTER_ARN = os.getenv('AURORA_CLUSTER_ARN')
SECRET_ARN = os.getenv('AURORA_SECRET_ARN')
DATABASE = os.getenv('AURORA_DATABASE', 'meridian')

# Travel catalog: 6 categories × 5 packages = 30 experiences (see travel_catalog.py)
from travel_catalog import TRAVEL_PRODUCTS as PRODUCTS



def get_bedrock_client():
    """Create Bedrock Runtime client for embedding generation"""
    return boto3.client(
        'bedrock-runtime',
        region_name=BEDROCK_REGION
    )


def get_rds_data_client():
    """Create RDS Data API client"""
    return boto3.client('rds-data', region_name=AURORA_REGION)


def generate_embedding(bedrock_client, text: str) -> list:
    """
    Generate embedding using Cohere Embed v4

    Args:
        bedrock_client: Boto3 Bedrock Runtime client
        text: Text to generate embedding for

    Returns:
        List of 1024 floats representing the embedding vector
    """
    request_body = {
        "texts": [text],
        "input_type": "search_document",
        "embedding_types": ["float"],
        "truncate": "RIGHT",
        "output_dimension": EMBEDDING_DIMENSION
    }

    response = bedrock_client.invoke_model(
        modelId=EMBEDDING_MODEL_ID,
        body=json.dumps(request_body),
        contentType="application/json",
        accept="application/json"
    )

    response_body = json.loads(response['body'].read())
    return response_body['embeddings']['float'][0]


def create_product_text(product: dict) -> str:
    """
    Create searchable text from product attributes for embedding generation
    
    Args:
        product: Product dictionary
        
    Returns:
        Combined text string for embedding
    """
    parts = [
        product['name'],
        product['description'],
        f"Category: {product['category']}",
        f"Brand: {product['brand']}"
    ]
    
    if product.get('available_sizes'):
        parts.append(f"Available sizes: {', '.join(product['available_sizes'])}")
    
    return ". ".join(parts)


def seed_database():
    """
    Seed the Aurora PostgreSQL database with products and Cohere Embed v4 embeddings
    
    Requirements covered:
    - 2.7: Populate 30 travel packages across 6 categories
    - 2.8: Generate 1024-dimensional embeddings using Cohere Embed v4
    """
    console.print("\n[bold blue]🌱 Seeding Meridian Database[/bold blue]")
    console.print(f"[cyan]Embedding Model: {EMBEDDING_MODEL_ID}[/cyan]")
    console.print(f"[cyan]Embedding Dimension: {EMBEDDING_DIMENSION}[/cyan]")
    console.print(f"[cyan]Region: {BEDROCK_REGION}[/cyan]\n")
    
    if not CLUSTER_ARN or not SECRET_ARN:
        console.print("[red]❌ Missing AURORA_CLUSTER_ARN or AURORA_SECRET_ARN in .env[/red]")
        return
    
    # Initialize clients
    console.print("[yellow]Initializing Amazon Bedrock client...[/yellow]")
    try:
        bedrock_client = get_bedrock_client()
        rds_client = get_rds_data_client()
        console.print("[green]✅ Clients initialized[/green]\n")
    except Exception as e:
        console.print(f"[bold red]❌ Failed to initialize clients: {e}[/bold red]")
        raise
    
    # Clear existing products (for clean re-seeding)
    console.print("[yellow]Clearing existing product data...[/yellow]")
    try:
        rds_client.execute_statement(
            resourceArn=CLUSTER_ARN,
            secretArn=SECRET_ARN,
            database=DATABASE,
            sql="DELETE FROM order_items WHERE TRUE"
        )
        rds_client.execute_statement(
            resourceArn=CLUSTER_ARN,
            secretArn=SECRET_ARN,
            database=DATABASE,
            sql="DELETE FROM orders WHERE TRUE"
        )
        rds_client.execute_statement(
            resourceArn=CLUSTER_ARN,
            secretArn=SECRET_ARN,
            database=DATABASE,
            sql="DELETE FROM products WHERE TRUE"
        )
        console.print("[green]✅ Existing data cleared[/green]\n")
    except Exception as e:
        console.print(f"[yellow]⚠️  Could not clear data (tables may be empty): {e}[/yellow]\n")
    
    # Insert products with embeddings
    console.print(f"[yellow]Inserting {len(PRODUCTS)} products with embeddings...[/yellow]\n")
    
    successful = 0
    failed = 0
    
    for product in track(PRODUCTS, description="Processing products"):
        try:
            # Generate embedding for product
            product_text = create_product_text(product)
            embedding = generate_embedding(bedrock_client, product_text)
            
            # Format embedding as PostgreSQL array string
            embedding_str = '[' + ','.join(str(x) for x in embedding) + ']'
            
            # Insert product into database using RDS Data API (UPSERT)
            sql = """
                INSERT INTO products (
                    product_id, name, category, price, brand, description,
                    image_url, available_sizes, inventory, embedding
                ) VALUES (
                    :product_id, :name, :category, :price, :brand, :description,
                    :image_url, :available_sizes::jsonb, :inventory::jsonb, :embedding::vector
                )
                ON CONFLICT (product_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    category = EXCLUDED.category,
                    price = EXCLUDED.price,
                    brand = EXCLUDED.brand,
                    description = EXCLUDED.description,
                    image_url = EXCLUDED.image_url,
                    available_sizes = EXCLUDED.available_sizes,
                    inventory = EXCLUDED.inventory,
                    embedding = EXCLUDED.embedding
            """
            
            parameters = [
                {'name': 'product_id', 'value': {'stringValue': product['product_id']}},
                {'name': 'name', 'value': {'stringValue': product['name']}},
                {'name': 'category', 'value': {'stringValue': product['category']}},
                {'name': 'price', 'value': {'doubleValue': float(product['price'])}},
                {'name': 'brand', 'value': {'stringValue': product['brand']}},
                {'name': 'description', 'value': {'stringValue': product['description']}},
                {'name': 'image_url', 'value': {'stringValue': product['image_url']}},
                {'name': 'available_sizes', 'value': {'stringValue': json.dumps(product['available_sizes']) if product['available_sizes'] else 'null'}},
                {'name': 'inventory', 'value': {'stringValue': json.dumps(product['inventory'])}},
                {'name': 'embedding', 'value': {'stringValue': embedding_str}},
            ]
            
            rds_client.execute_statement(
                resourceArn=CLUSTER_ARN,
                secretArn=SECRET_ARN,
                database=DATABASE,
                sql=sql,
                parameters=parameters
            )
            
            successful += 1
            
        except Exception as e:
            console.print(f"[red]❌ Failed to process {product['product_id']}: {e}[/red]")
            failed += 1
            continue
    
    # Display summary
    console.print("\n[bold green]🎉 Seeding Complete![/bold green]\n")
    
    summary_table = Table(title="Seed Data Summary")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="green")
    
    summary_table.add_row("Total Products", str(len(PRODUCTS)))
    summary_table.add_row("Successfully Inserted", str(successful))
    summary_table.add_row("Failed", str(failed))
    summary_table.add_row("Embedding Model", EMBEDDING_MODEL_ID)
    summary_table.add_row("Embedding Dimension", str(EMBEDDING_DIMENSION))
    
    console.print(summary_table)
    
    # Display category breakdown
    console.print("\n")
    category_table = Table(title="Products by Category")
    category_table.add_column("Category", style="cyan")
    category_table.add_column("Count", style="green")
    
    categories = {}
    for product in PRODUCTS:
        cat = product['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    for cat, count in sorted(categories.items()):
        category_table.add_row(cat, str(count))
    
    console.print(category_table)
    
    if failed > 0:
        console.print(f"\n[yellow]⚠️  {failed} products failed to insert. Check logs above.[/yellow]")
    else:
        console.print("\n[green]✅ All products seeded successfully with embeddings![/green]")


def verify_embeddings():
    """Verify that all products have embeddings with correct dimensions"""
    console.print("\n[bold blue]🔍 Verifying Embeddings[/bold blue]\n")
    
    if not CLUSTER_ARN or not SECRET_ARN:
        console.print("[red]❌ Missing AURORA_CLUSTER_ARN or AURORA_SECRET_ARN in .env[/red]")
        return
    
    rds_client = get_rds_data_client()
    
    # Check total products
    result = rds_client.execute_statement(
        resourceArn=CLUSTER_ARN,
        secretArn=SECRET_ARN,
        database=DATABASE,
        sql="SELECT COUNT(*) FROM products"
    )
    total = result['records'][0][0]['longValue']
    
    # Check products with embeddings
    result = rds_client.execute_statement(
        resourceArn=CLUSTER_ARN,
        secretArn=SECRET_ARN,
        database=DATABASE,
        sql="SELECT COUNT(*) FROM products WHERE embedding IS NOT NULL"
    )
    with_embeddings = result['records'][0][0]['longValue']
    
    # Check embedding dimensions
    result = rds_client.execute_statement(
        resourceArn=CLUSTER_ARN,
        secretArn=SECRET_ARN,
        database=DATABASE,
        sql="""
            SELECT product_id, name, vector_dims(embedding) as dims
            FROM products
            WHERE embedding IS NOT NULL
            LIMIT 5
        """
    )
    sample_products = [(r[0]['stringValue'], r[1]['stringValue'], r[2]['longValue']) for r in result.get('records', [])]
    
    # Check category distribution
    result = rds_client.execute_statement(
        resourceArn=CLUSTER_ARN,
        secretArn=SECRET_ARN,
        database=DATABASE,
        sql="""
            SELECT category, COUNT(*) as count
            FROM products
            GROUP BY category
            ORDER BY category
        """
    )
    category_counts = [(r[0]['stringValue'], r[1]['longValue']) for r in result.get('records', [])]
    
    # Display verification results
    verify_table = Table(title="Embedding Verification")
    verify_table.add_column("Check", style="cyan")
    verify_table.add_column("Result", style="green")
    
    verify_table.add_row("Total Products", str(total))
    verify_table.add_row("Products with Embeddings", str(with_embeddings))
    verify_table.add_row("Expected Dimension", str(EMBEDDING_DIMENSION))
    
    console.print(verify_table)
    
    # Show sample products with dimensions
    console.print("\n")
    sample_table = Table(title="Sample Products (First 5)")
    sample_table.add_column("Product ID", style="cyan")
    sample_table.add_column("Name", style="white")
    sample_table.add_column("Embedding Dims", style="green")
    
    for product_id, name, dims in sample_products:
        status = "✅" if dims == EMBEDDING_DIMENSION else "❌"
        sample_table.add_row(product_id, name[:40], f"{dims} {status}")
    
    console.print(sample_table)
    
    # Show category distribution
    console.print("\n")
    cat_table = Table(title="Category Distribution")
    cat_table.add_column("Category", style="cyan")
    cat_table.add_column("Count", style="green")
    
    for category, count in category_counts:
        cat_table.add_row(category, str(count))
    
    console.print(cat_table)
    
    # Final status
    if with_embeddings == total and total == 30:
        console.print("\n[bold green]✅ All 30 products have embeddings![/bold green]")
    else:
        console.print(f"\n[bold yellow]⚠️  Expected 30 products, found {total} ({with_embeddings} with embeddings)[/bold yellow]")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        verify_embeddings()
    else:
        seed_database()
        console.print("\n[cyan]Run with --verify to check embedding status[/cyan]")
