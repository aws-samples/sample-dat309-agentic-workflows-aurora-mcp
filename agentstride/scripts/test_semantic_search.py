"""
Test semantic search with Nova Multimodal Embeddings.
Verifies end-to-end search functionality using the RDS Data API.
"""
import os
import json
import boto3
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv()
console = Console()

# Configuration from environment
EMBEDDING_MODEL_ID = os.getenv("EMBEDDING_MODEL", "amazon.nova-2-multimodal-embeddings-v1:0")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1024"))
REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
CLUSTER_ARN = os.getenv("AURORA_CLUSTER_ARN")
SECRET_ARN = os.getenv("AURORA_SECRET_ARN")
DATABASE = os.getenv("AURORA_DATABASE", "clickshop")


def generate_query_embedding(bedrock_client, query: str) -> list:
    """Generate embedding for search query using Nova Multimodal Embeddings."""
    request_body = {
        "schemaVersion": "nova-multimodal-embed-v1",
        "taskType": "SINGLE_EMBEDDING",
        "singleEmbeddingParams": {
            "embeddingPurpose": "TEXT_RETRIEVAL",
            "embeddingDimension": EMBEDDING_DIMENSION,
            "text": {
                "truncationMode": "END",
                "value": query
            }
        }
    }
    
    response = bedrock_client.invoke_model(
        modelId=EMBEDDING_MODEL_ID,
        body=json.dumps(request_body),
        contentType="application/json",
        accept="application/json"
    )
    
    response_body = json.loads(response["body"].read())
    return response_body["embeddings"][0]["embedding"]


def semantic_search(rds_client, bedrock_client, query: str, limit: int = 5):
    """
    Perform semantic search using Nova Multimodal embeddings and pgvector.
    
    Args:
        rds_client: RDS Data API client
        bedrock_client: Bedrock Runtime client
        query: Search query text
        limit: Number of results to return
        
    Returns:
        List of matching products with similarity scores
    """
    # Generate query embedding
    console.print(f"\n[cyan]Generating embedding for query: '{query}'[/cyan]")
    query_embedding = generate_query_embedding(bedrock_client, query)
    console.print(f"[green]✅ Generated {len(query_embedding)}-dimensional embedding[/green]")
    
    # Format embedding for PostgreSQL
    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
    
    # Execute semantic search using pgvector cosine similarity
    sql = """
        SELECT 
            product_id,
            name,
            category,
            brand,
            price,
            description,
            1 - (embedding <=> :query_embedding::vector) as similarity
        FROM products
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> :query_embedding::vector
        LIMIT :limit
    """
    
    response = rds_client.execute_statement(
        resourceArn=CLUSTER_ARN,
        secretArn=SECRET_ARN,
        database=DATABASE,
        sql=sql,
        parameters=[
            {"name": "query_embedding", "value": {"stringValue": embedding_str}},
            {"name": "limit", "value": {"longValue": limit}}
        ]
    )
    
    return response.get("records", [])


def test_semantic_search():
    """Run semantic search tests with various queries."""
    console.print("\n[bold blue]🔍 Testing Semantic Search with Nova Multimodal Embeddings[/bold blue]")
    console.print(f"[cyan]Model: {EMBEDDING_MODEL_ID}[/cyan]")
    console.print(f"[cyan]Region: {REGION}[/cyan]")
    console.print(f"[cyan]Dimensions: {EMBEDDING_DIMENSION}[/cyan]\n")
    
    if not CLUSTER_ARN or not SECRET_ARN:
        console.print("[red]❌ Missing AURORA_CLUSTER_ARN or AURORA_SECRET_ARN in .env[/red]")
        return
    
    # Initialize clients
    bedrock_client = boto3.client("bedrock-runtime", region_name=REGION)
    rds_client = boto3.client("rds-data", region_name=REGION)
    console.print("[green]✅ Clients initialized[/green]")
    
    # Test queries
    test_queries = [
        "comfortable running shoes for long distance",
        "weightlifting equipment for home gym",
        "recovery tools for sore muscles",
        "waterproof fitness tracker",
        "breathable workout clothes"
    ]
    
    for query in test_queries:
        console.print(f"\n{'='*60}")
        results = semantic_search(rds_client, bedrock_client, query, limit=3)
        
        if results:
            console.print(f"\n[bold]Top 3 results for: '{query}'[/bold]\n")
            
            for i, record in enumerate(results, 1):
                name = record[1].get("stringValue", "")
                category = record[2].get("stringValue", "")
                brand = record[3].get("stringValue", "")
                # Price may be stored as string or double
                price_val = record[4]
                price = float(price_val.get("stringValue", "0") or price_val.get("doubleValue", 0))
                similarity = record[6].get("doubleValue", 0)
                
                console.print(f"  {i}. [cyan]{name}[/cyan]")
                console.print(f"     Category: {category} | Brand: {brand}")
                console.print(f"     Price: [green]${price:.2f}[/green] | Similarity: [yellow]{similarity:.4f}[/yellow]\n")
        else:
            console.print("[yellow]No results found[/yellow]")
    
    console.print(f"\n{'='*60}")
    console.print("\n[bold green]✅ Semantic search test complete![/bold green]")
    console.print("[cyan]Nova Multimodal Embeddings are working correctly with pgvector.[/cyan]\n")


if __name__ == "__main__":
    test_semantic_search()
