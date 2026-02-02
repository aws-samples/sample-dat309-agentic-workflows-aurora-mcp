"""
Generate vector embeddings for products using Amazon Nova Multimodal Embeddings.
Uses amazon.nova-2-multimodal-embeddings-v1:0 with 1024 dimensions.
"""
import os
import sys
import json
import boto3
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import track

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()
console = Console()

# Nova Multimodal Embeddings configuration
MODEL_ID = os.getenv("EMBEDDING_MODEL", "amazon.nova-2-multimodal-embeddings-v1:0")
DIMENSIONS = int(os.getenv("EMBEDDING_DIMENSION", "1024"))


def generate_text_embedding(bedrock_client, text: str) -> list:
    """Generate embedding for text using Nova Multimodal Embeddings."""
    request_body = {
        "schemaVersion": "nova-multimodal-embed-v1",
        "taskType": "SINGLE_EMBEDDING",
        "singleEmbeddingParams": {
            "embeddingPurpose": "TEXT_RETRIEVAL",
            "embeddingDimension": DIMENSIONS,
            "text": {
                "truncationMode": "END",
                "value": text
            }
        }
    }
    
    response = bedrock_client.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(request_body),
        contentType="application/json",
        accept="application/json"
    )
    
    response_body = json.loads(response["body"].read())
    return response_body["embeddings"][0]["embedding"]


def generate_embeddings():
    """Generate and store embeddings for all products using RDS Data API."""
    console.print("\n[bold blue]🤖 Generating Product Embeddings[/bold blue]")
    console.print(f"Model: {MODEL_ID}")
    console.print(f"Dimensions: {DIMENSIONS}\n")
    
    # Initialize clients
    region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    bedrock_client = boto3.client("bedrock-runtime", region_name=region)
    rds_client = boto3.client("rds-data", region_name=region)
    
    cluster_arn = os.getenv("AURORA_CLUSTER_ARN")
    secret_arn = os.getenv("AURORA_SECRET_ARN")
    database = os.getenv("AURORA_DATABASE", "clickshop")
    
    if not cluster_arn or not secret_arn:
        console.print("[red]❌ Missing AURORA_CLUSTER_ARN or AURORA_SECRET_ARN[/red]")
        return
    
    console.print("[green]✅ Clients initialized[/green]\n")
    
    # Get all products - regenerate all embeddings
    response = rds_client.execute_statement(
        resourceArn=cluster_arn,
        secretArn=secret_arn,
        database=database,
        sql="""
            SELECT product_id, name, description, category, brand
            FROM products
        """
    )
    
    products = response.get("records", [])
    console.print(f"[yellow]Generating embeddings for {len(products)} products...[/yellow]\n")
    
    if not products:
        console.print("[yellow]No products found in database.[/yellow]")
        return
    
    success_count = 0
    for record in track(products, description="Processing"):
        try:
            # Extract fields from RDS Data API response format
            product_id = record[0].get("stringValue")
            name = record[1].get("stringValue", "")
            description = record[2].get("stringValue", "")
            category = record[3].get("stringValue", "")
            brand = record[4].get("stringValue", "")
            
            # Create searchable text by combining fields
            search_text = f"{name}. {description}. Category: {category}. Brand: {brand}"
            
            # Generate embedding using Titan Text Embeddings v2
            embedding = generate_text_embedding(bedrock_client, search_text)
            
            # Store in database - convert to PostgreSQL array format
            embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"
            
            rds_client.execute_statement(
                resourceArn=cluster_arn,
                secretArn=secret_arn,
                database=database,
                sql="""
                    UPDATE products
                    SET embedding = :embedding::vector
                    WHERE product_id = :product_id
                """,
                parameters=[
                    {"name": "embedding", "value": {"stringValue": embedding_str}},
                    {"name": "product_id", "value": {"stringValue": product_id}}
                ]
            )
            success_count += 1
            
        except Exception as e:
            console.print(f"[red]Error processing {product_id}: {e}[/red]")
    
    console.print(f"\n[green]✅ Generated embeddings for {success_count} products![/green]")
    
    # Verify
    response = rds_client.execute_statement(
        resourceArn=cluster_arn,
        secretArn=secret_arn,
        database=database,
        sql="SELECT COUNT(*) FROM products WHERE embedding IS NOT NULL"
    )
    count = response["records"][0][0].get("longValue", 0)
    console.print(f"[green]✅ {count} products now have embeddings[/green]")


if __name__ == "__main__":
    generate_embeddings()
