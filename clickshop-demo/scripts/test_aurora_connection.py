"""Test Aurora PostgreSQL connection"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Testing Aurora PostgreSQL connection with psycopg3...")
print(f"Host: {os.getenv('AURORA_HOST')}")
print(f"Database: {os.getenv('AURORA_DATABASE')}")
print(f"Port: {os.getenv('AURORA_PORT')}")
print()

# Check if credentials are loaded
if not os.getenv('AURORA_HOST'):
    print("❌ Error: .env file not found or not configured")
    print("Please create .env file with Aurora credentials")
    sys.exit(1)

try:
    import psycopg
    
    # Connect using psycopg3
    conn = psycopg.connect(
        host=os.getenv('AURORA_HOST'),
        port=os.getenv('AURORA_PORT'),
        dbname=os.getenv('AURORA_DATABASE'),
        user=os.getenv('AURORA_USERNAME'),
        password=os.getenv('AURORA_PASSWORD'),
        connect_timeout=10
    )
    
    print("✅ Connection successful!")
    
    # Test query
    with conn.cursor() as cur:
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"✅ PostgreSQL version: {version[:60]}...")
        
        # Check for pgvector extension
        cur.execute("""
            SELECT EXISTS (
                SELECT 1 FROM pg_extension WHERE extname = 'vector'
            );
        """)
        has_vector = cur.fetchone()[0]
        
        if has_vector:
            print("✅ pgvector extension is installed")
            
            # Get vector extension version
            cur.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector';")
            vector_version = cur.fetchone()[0]
            print(f"✅ pgvector version: {vector_version}")
        else:
            print("⚠️  pgvector extension not installed (will install in next step)")
    
    conn.close()
    print("\n🎉 Aurora PostgreSQL is ready to use!")
    
except ImportError:
    print("❌ psycopg3 not installed")
    print("Run: pip install 'psycopg[binary,pool]'")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\nTroubleshooting:")
    print("1. Verify Aurora cluster is running")
    print("2. Check security group allows your IP")
    print("3. Confirm credentials in .env are correct")
    print("4. Test with psql CLI:")
    print(f"   psql -h {os.getenv('AURORA_HOST')} -U {os.getenv('AURORA_USERNAME')} -d {os.getenv('AURORA_DATABASE')}")
    sys.exit(1)
