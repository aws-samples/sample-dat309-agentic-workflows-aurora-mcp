"""
Generate vector embeddings for products using sentence-transformers
This enables semantic search in Month 3 demo
"""
import os
import psycopg
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from rich.console import Console
from rich.progress import track

load_dotenv()
console = Console()

def generate_embeddings():
    """Generate and store embeddings for all products"""
    console.print("\n[bold blue]🤖 Generating Product Embeddings[/bold blue]")
    console.print("Model: all-MiniLM-L6-v2 (384 dimensions)\n")
    
    # Load embedding model
    console.print("[yellow]Loading sentence transformer model...[/yellow]")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    console.print("[green]✅ Model loaded[/green]\n")
    
    # Connect to Aurora
    conn = psycopg.connect(
        host=os.getenv('AURORA_HOST'),
        port=os.getenv('AURORA_PORT'),
        dbname=os.getenv('AURORA_DATABASE'),
        user=os.getenv('AURORA_USERNAME'),
        password=os.getenv('AURORA_PASSWORD')
    )
    
    with conn.cursor() as cur:
        # Get all products
        cur.execute("""
            SELECT product_id, name, description, category, brand
            FROM products
            WHERE embedding IS NULL
        """)
        products = cur.fetchall()
        
        console.print(f"[yellow]Generating embeddings for {len(products)} products...[/yellow]\n")
        
        for product in track(products, description="Processing"):
            product_id, name, description, category, brand = product
            
            # Create searchable text by combining fields
            search_text = f"{name}. {description}. Category: {category}. Brand: {brand}"
            
            # Generate embedding
            embedding = model.encode(search_text)
            
            # Store in database
            cur.execute("""
                UPDATE products
                SET embedding = %s::vector
                WHERE product_id = %s
            """, (embedding.tolist(), product_id))
        
        conn.commit()
        
        console.print("\n[green]✅ All embeddings generated and stored![/green]")
        
        # Verify
        cur.execute("SELECT COUNT(*) FROM products WHERE embedding IS NOT NULL")
        count = cur.fetchone()[0]
        console.print(f"[green]✅ {count} products now have embeddings[/green]")
    
    conn.close()

if __name__ == "__main__":
    generate_embeddings()
