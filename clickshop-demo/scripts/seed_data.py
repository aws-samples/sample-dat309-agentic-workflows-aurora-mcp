"""
Seed data script for ClickShop Enhancement
Populates Aurora PostgreSQL with 30 products across 6 categories
Generates 1024-dimensional embeddings using Amazon Nova Multimodal Embeddings

Requirements covered:
- 2.7: Populate 30 products across 6 categories
- 2.8: Generate 1024-dimensional embeddings using Amazon Nova Multimodal Embeddings
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

# Nova Multimodal Embeddings Configuration
EMBEDDING_MODEL_ID = os.getenv("EMBEDDING_MODEL", "amazon.nova-2-multimodal-embeddings-v1:0")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1024"))
BEDROCK_REGION = os.getenv('BEDROCK_REGION', 'us-east-1')

# RDS Data API Configuration
CLUSTER_ARN = os.getenv('AURORA_CLUSTER_ARN')
SECRET_ARN = os.getenv('AURORA_SECRET_ARN')
DATABASE = os.getenv('AURORA_DATABASE', 'clickshop')

# Product catalog: 6 categories with 5 products each = 30 total products
# Image URLs selected to match actual product brands and types
PRODUCTS = [
    # Category 1: Running Shoes (5 products)
    {
        "product_id": "RUN-001",
        "name": "Nike Air Zoom Pegasus 41",
        "category": "Running Shoes",
        "price": 139.99,
        "brand": "Nike",
        "description": "Responsive cushioning for everyday runs. Features Zoom Air units in the forefoot and heel for a smooth, springy ride. Breathable mesh upper with Flywire cables for secure fit.",
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=300&fit=crop",  # Red Nike running shoe
        "available_sizes": ["7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11", "11.5", "12"],
        "inventory": {"7": 5, "8": 12, "9": 15, "10": 18, "11": 10, "12": 6}
    },
    {
        "product_id": "RUN-002",
        "name": "Nike Blazer Mid '77",
        "category": "Training Shoes",
        "price": 119.99,
        "brand": "Nike",
        "description": "Classic Nike Blazer Mid with bold gradient colorway. Lightweight cushioning for all-day comfort. High-top design for ankle support.",
        "image_url": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=400&h=300&fit=crop",  # Colorful Nike shoe
        "available_sizes": ["7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11", "11.5", "12"],
        "inventory": {"7": 8, "8": 14, "9": 20, "10": 22, "11": 12, "12": 7}
    },
    {
        "product_id": "RUN-003",
        "name": "Nike Vomero 18",
        "category": "Running Shoes",
        "price": 149.99,
        "brand": "Nike",
        "description": "Smooth transitions and soft cushioning for neutral runners. ZoomX foam provides a soft yet responsive feel. Engineered mesh upper for breathability.",
        "image_url": "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=400&h=300&fit=crop",  # White/grey Nike running shoe
        "available_sizes": ["7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11", "11.5", "12", "13"],
        "inventory": {"7": 6, "8": 10, "9": 16, "10": 14, "11": 8, "12": 5, "13": 3}
    },
    {
        "product_id": "RUN-004",
        "name": "Nike Air Max 1",
        "category": "Running Shoes",
        "price": 149.99,
        "brand": "Nike",
        "description": "Iconic Nike Air Max 1 with visible Air cushioning. Premium leather and mesh upper for breathability. Classic orange and white colorway. Waffle outsole for traction.",
        "image_url": "https://images.unsplash.com/photo-1600185365926-3a2ce3cdb9eb?w=400&h=300&fit=crop",  # Orange/white Nike Air Max 1
        "available_sizes": ["7", "8", "8.5", "9", "9.5", "10", "10.5", "11", "12"],
        "inventory": {"7": 4, "8": 9, "9": 13, "10": 15, "11": 7, "12": 4}
    },
    {
        "product_id": "RUN-005",
        "name": "New Balance Fresh Foam X 1080v13",
        "category": "Running Shoes",
        "price": 164.99,
        "brand": "New Balance",
        "description": "Plush cushioning meets responsive performance. Fresh Foam X midsole with Hypoknit upper for stretch and support. Blown rubber outsole for durability.",
        "image_url": "https://images.unsplash.com/photo-1539185441755-769473a23570?w=400&h=300&fit=crop",  # Gray/white running shoe
        "available_sizes": ["7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11", "11.5", "12", "13"],
        "inventory": {"7": 7, "8": 11, "9": 18, "10": 20, "11": 9, "12": 6, "13": 2}
    },
    # Category 2: Training Shoes (5 products)
    {
        "product_id": "TRN-001",
        "name": "Nike Metcon 9",
        "category": "Training Shoes",
        "price": 149.99,
        "brand": "Nike",
        "description": "Built for high-intensity training and weightlifting. Wide, flat heel for stability during lifts. Rope-wrap outsole for rope climbs. Breathable mesh upper.",
        "image_url": "https://images.unsplash.com/photo-1562183241-b937e95585b6?w=400&h=300&fit=crop",  # Black Nike training shoe
        "available_sizes": ["7", "8", "8.5", "9", "9.5", "10", "10.5", "11", "12"],
        "inventory": {"7": 6, "8": 10, "9": 14, "10": 16, "11": 8, "12": 5}
    },
    {
        "product_id": "TRN-002",
        "name": "Reebok Nano X4",
        "category": "Training Shoes",
        "price": 139.99,
        "brand": "Reebok",
        "description": "Versatile CrossFit training shoe with Floatride Energy Foam. Low-cut design for mobility. Flexweave knit upper for durability and breathability.",
        "image_url": "https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?w=400&h=300&fit=crop",  # White training shoe
        "available_sizes": ["7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11", "12"],
        "inventory": {"7": 5, "8": 12, "9": 15, "10": 13, "11": 7, "12": 4}
    },
    {
        "product_id": "TRN-003",
        "name": "Nike SB Dunk Low",
        "category": "Training Shoes",
        "price": 119.99,
        "brand": "Nike",
        "description": "Classic Nike SB Dunk Low with clean white colorway. Padded collar for comfort. Zoom Air insole for impact protection. Durable rubber outsole with herringbone pattern.",
        "image_url": "https://images.unsplash.com/photo-1460353581641-37baddab0fa2?w=400&h=300&fit=crop",  # White Nike sneaker
        "available_sizes": ["8", "8.5", "9", "9.5", "10", "10.5", "11", "11.5", "12", "13"],
        "inventory": {"8": 8, "9": 12, "10": 18, "11": 14, "12": 9, "13": 4}
    },
    {
        "product_id": "TRN-004",
        "name": "Nike Air Max 90",
        "category": "Training Shoes",
        "price": 139.99,
        "brand": "Nike",
        "description": "Iconic Nike Air Max 90 with visible Air cushioning. Premium leather and mesh upper for breathability. Waffle outsole for traction. Classic colorway with bold design.",
        "image_url": "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=400&h=300&fit=crop",  # White Nike Air Max
        "available_sizes": ["7", "8", "9", "10", "11", "12"],
        "inventory": {"7": 4, "8": 8, "9": 11, "10": 12, "11": 6, "12": 3}
    },
    {
        "product_id": "TRN-005",
        "name": "Puma Fuse 3.0",
        "category": "Training Shoes",
        "price": 109.99,
        "brand": "Puma",
        "description": "Affordable versatility for gym workouts. PROFOAM midsole for cushioning. Rubber outsole with pivot points. Mesh upper with synthetic overlays.",
        "image_url": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=400&h=300&fit=crop",  # Black/white training shoe
        "available_sizes": ["7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11", "12"],
        "inventory": {"7": 10, "8": 15, "9": 20, "10": 18, "11": 12, "12": 8}
    },
    # Category 3: Fitness Equipment (5 products)
    {
        "product_id": "EQP-001",
        "name": "Bowflex SelectTech 552 Dumbbells",
        "category": "Fitness Equipment",
        "price": 549.99,
        "brand": "Bowflex",
        "description": "Adjustable dumbbells replacing 15 sets of weights. Range from 5 to 52.5 lbs per dumbbell. Quick dial adjustment system. Space-saving design for home gyms.",
        "image_url": "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=400&h=300&fit=crop",  # Dumbbells
        "available_sizes": None,
        "inventory": {"quantity": 25}
    },
    {
        "product_id": "EQP-002",
        "name": "TRX PRO4 Suspension Trainer",
        "category": "Fitness Equipment",
        "price": 249.99,
        "brand": "TRX",
        "description": "Professional-grade suspension training system. Adjustable foot cradles and rubber handles. Includes door anchor, suspension anchor, and mesh carry bag.",
        "image_url": "https://images.unsplash.com/photo-1598289431512-b97b0917affc?w=400&h=300&fit=crop",  # Suspension trainer straps
        "available_sizes": None,
        "inventory": {"quantity": 40}
    },
    {
        "product_id": "EQP-003",
        "name": "Rogue Echo Bike",
        "category": "Fitness Equipment",
        "price": 795.00,
        "brand": "Rogue",
        "description": "Air resistance fan bike for intense cardio. Steel frame construction. Belt-driven fan for smooth operation. LCD console tracks calories, distance, and heart rate.",
        "image_url": "https://images.unsplash.com/photo-1591291621164-2c6367723315?w=400&h=300&fit=crop",  # Exercise bike
        "available_sizes": None,
        "inventory": {"quantity": 12}
    },
    {
        "product_id": "EQP-004",
        "name": "Concept2 RowErg",
        "category": "Fitness Equipment",
        "price": 990.00,
        "brand": "Concept2",
        "description": "Gold standard indoor rowing machine. PM5 performance monitor with Bluetooth. Air resistance flywheel. Separates for easy storage. Used by Olympic athletes.",
        "image_url": "https://images.unsplash.com/photo-1519505907962-0a6cb0167c73?w=400&h=300&fit=crop",  # Rowing machine
        "available_sizes": None,
        "inventory": {"quantity": 8}
    },
    {
        "product_id": "EQP-005",
        "name": "Peloton Guide",
        "category": "Fitness Equipment",
        "price": 295.00,
        "brand": "Peloton",
        "description": "AI-powered strength training camera. Tracks your movements and counts reps. Connects to your TV. Access to Peloton strength classes. Form feedback in real-time.",
        "image_url": "https://images.unsplash.com/photo-1576678927484-cc907957088c?w=400&h=300&fit=crop",  # Home gym setup
        "available_sizes": None,
        "inventory": {"quantity": 30}
    },
    # Category 4: Apparel (5 products)
    {
        "product_id": "APP-001",
        "name": "Lululemon Metal Vent Tech Shirt",
        "category": "Apparel",
        "price": 78.00,
        "brand": "Lululemon",
        "description": "Anti-stink training shirt with seamless construction. Silverescent technology inhibits odor. Four-way stretch fabric. Mesh ventilation panels.",
        "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=300&fit=crop",  # Athletic t-shirt
        "available_sizes": ["XS", "S", "M", "L", "XL", "XXL"],
        "inventory": {"XS": 8, "S": 15, "M": 25, "L": 22, "XL": 12, "XXL": 6}
    },
    {
        "product_id": "APP-002",
        "name": "Nike Dri-FIT Running Shorts",
        "category": "Apparel",
        "price": 45.00,
        "brand": "Nike",
        "description": "Lightweight running shorts with built-in brief. Dri-FIT technology wicks sweat. Side mesh panels for ventilation. Zippered back pocket for keys.",
        "image_url": "https://images.unsplash.com/photo-1591195853828-11db59a44f6b?w=400&h=300&fit=crop",  # Athletic shorts
        "available_sizes": ["S", "M", "L", "XL", "XXL"],
        "inventory": {"S": 20, "M": 30, "L": 28, "XL": 15, "XXL": 8}
    },
    {
        "product_id": "APP-003",
        "name": "Under Armour HeatGear Compression Leggings",
        "category": "Apparel",
        "price": 55.00,
        "brand": "Under Armour",
        "description": "Second-skin fit compression tights. HeatGear fabric keeps you cool. UPF 30+ sun protection. Flatlock seams prevent chafing. Hidden waistband pocket.",
        "image_url": "https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=400&h=300&fit=crop",  # Compression leggings
        "available_sizes": ["XS", "S", "M", "L", "XL"],
        "inventory": {"XS": 12, "S": 18, "M": 24, "L": 20, "XL": 10}
    },
    {
        "product_id": "APP-004",
        "name": "Gymshark Vital Seamless Sports Bra",
        "category": "Apparel",
        "price": 42.00,
        "brand": "Gymshark",
        "description": "Medium support seamless sports bra. Ribbed fabric with DRY technology. Removable padding. Racerback design for freedom of movement.",
        "image_url": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=300&fit=crop",  # Sports bra workout
        "available_sizes": ["XS", "S", "M", "L", "XL"],
        "inventory": {"XS": 15, "S": 22, "M": 28, "L": 18, "XL": 8}
    },
    {
        "product_id": "APP-005",
        "name": "Patagonia Nano Puff Jacket",
        "category": "Apparel",
        "price": 229.00,
        "brand": "Patagonia",
        "description": "Lightweight insulated jacket for outdoor training. 60g PrimaLoft Gold insulation. Windproof and water-resistant shell. Packs into internal chest pocket.",
        "image_url": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=400&h=300&fit=crop",  # Puffer jacket
        "available_sizes": ["XS", "S", "M", "L", "XL", "XXL"],
        "inventory": {"XS": 6, "S": 10, "M": 14, "L": 12, "XL": 8, "XXL": 4}
    },
    # Category 5: Accessories (5 products)
    {
        "product_id": "ACC-001",
        "name": "Apple Watch Ultra 2",
        "category": "Accessories",
        "price": 799.00,
        "brand": "Apple",
        "description": "Advanced fitness smartwatch with precision GPS. 36-hour battery life. Water resistant to 100m. Blood oxygen and ECG monitoring. Titanium case.",
        "image_url": "https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=400&h=300&fit=crop",  # Apple Watch
        "available_sizes": ["49mm"],
        "inventory": {"49mm": 20}
    },
    {
        "product_id": "ACC-002",
        "name": "Garmin Forerunner 965",
        "category": "Accessories",
        "price": 599.99,
        "brand": "Garmin",
        "description": "Premium GPS running watch with AMOLED display. Training readiness and race predictor. Music storage for 2000 songs. 23-day battery in smartwatch mode.",
        "image_url": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=400&h=300&fit=crop",  # Sports watch
        "available_sizes": ["One Size"],
        "inventory": {"One Size": 15}
    },
    {
        "product_id": "ACC-003",
        "name": "Beats Fit Pro Earbuds",
        "category": "Accessories",
        "price": 199.99,
        "brand": "Beats",
        "description": "True wireless earbuds with secure-fit wingtips. Active Noise Cancellation. Spatial Audio with head tracking. IPX4 sweat and water resistant.",
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400&h=300&fit=crop",  # Wireless earbuds
        "available_sizes": ["One Size"],
        "inventory": {"One Size": 35}
    },
    {
        "product_id": "ACC-004",
        "name": "Hydro Flask 32oz Wide Mouth",
        "category": "Accessories",
        "price": 44.95,
        "brand": "Hydro Flask",
        "description": "Insulated stainless steel water bottle. TempShield keeps drinks cold 24 hours. Flex Cap with honeycomb insulation. BPA-free and dishwasher safe.",
        "image_url": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=400&h=300&fit=crop",  # Water bottle
        "available_sizes": ["32oz"],
        "inventory": {"32oz": 50}
    },
    {
        "product_id": "ACC-005",
        "name": "Theragun Mini 2.0",
        "category": "Accessories",
        "price": 199.00,
        "brand": "Therabody",
        "description": "Portable percussion massage device. QuietForce Technology for silent operation. 3 speed settings. 150-minute battery life. Weighs only 1.4 lbs.",
        "image_url": "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400&h=300&fit=crop",  # Massage device/recovery
        "available_sizes": ["One Size"],
        "inventory": {"One Size": 28}
    },
    # Category 6: Recovery (5 products)
    {
        "product_id": "REC-001",
        "name": "Hyperice Normatec 3 Legs",
        "category": "Recovery",
        "price": 799.00,
        "brand": "Hyperice",
        "description": "Dynamic air compression leg recovery system. 7 levels of intensity. Bluetooth app control. ZoneBoost technology for targeted relief. Used by pro athletes.",
        "image_url": "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=400&h=300&fit=crop",  # Leg recovery/compression
        "available_sizes": ["One Size"],
        "inventory": {"One Size": 10}
    },
    {
        "product_id": "REC-002",
        "name": "TriggerPoint GRID Foam Roller",
        "category": "Recovery",
        "price": 39.99,
        "brand": "TriggerPoint",
        "description": "Multi-density foam roller for muscle recovery. GRID pattern mimics therapist's hands. Hollow core for durability. 13-inch length for targeted rolling.",
        "image_url": "https://images.unsplash.com/photo-1600881333168-2ef49b341f30?w=400&h=300&fit=crop",  # Foam roller
        "available_sizes": ["13 inch", "26 inch"],
        "inventory": {"13 inch": 45, "26 inch": 25}
    },
    {
        "product_id": "REC-003",
        "name": "Compex Sport Elite 3.0",
        "category": "Recovery",
        "price": 449.99,
        "brand": "Compex",
        "description": "Muscle stimulator for recovery and performance. 9 programs including warm-up and recovery. FDA cleared. Wireless PODs for freedom of movement.",
        "image_url": "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=400&h=300&fit=crop",  # Muscle stimulator/recovery device
        "available_sizes": ["One Size"],
        "inventory": {"One Size": 12}
    },
    {
        "product_id": "REC-004",
        "name": "Chirp Wheel+ 3-Pack",
        "category": "Recovery",
        "price": 99.99,
        "brand": "Chirp",
        "description": "Back roller wheels in 3 sizes for spine relief. Padded PVC exterior. Targets muscles around the spine. Includes 12, 10, and 6-inch wheels.",
        "image_url": "https://images.unsplash.com/photo-1518310383802-640c2de311b2?w=400&h=300&fit=crop",  # Back roller/yoga wheel
        "available_sizes": ["3-Pack"],
        "inventory": {"3-Pack": 30}
    },
    {
        "product_id": "REC-005",
        "name": "Epsom Salt Recovery Soak 5lb",
        "category": "Recovery",
        "price": 24.99,
        "brand": "Dr Teal's",
        "description": "Pure magnesium sulfate bath soak with eucalyptus. Relieves muscle aches and tension. Promotes relaxation and sleep. 5-pound resealable bag.",
        "image_url": "https://images.unsplash.com/photo-1540555700478-4be289fbecef?w=400&h=300&fit=crop",  # Bath salts/spa
        "available_sizes": ["5lb"],
        "inventory": {"5lb": 60}
    }
]


def get_bedrock_client():
    """Create Bedrock Runtime client for embedding generation"""
    return boto3.client(
        'bedrock-runtime',
        region_name=BEDROCK_REGION
    )


def get_rds_data_client():
    """Create RDS Data API client"""
    return boto3.client('rds-data', region_name=BEDROCK_REGION)


def generate_embedding(bedrock_client, text: str) -> list:
    """
    Generate embedding using Amazon Nova Multimodal Embeddings
    
    Args:
        bedrock_client: Boto3 Bedrock Runtime client
        text: Text to generate embedding for
        
    Returns:
        List of 1024 floats representing the embedding vector
    """
    request_body = {
        "schemaVersion": "nova-multimodal-embed-v1",
        "taskType": "SINGLE_EMBEDDING",
        "singleEmbeddingParams": {
            "embeddingPurpose": "TEXT_RETRIEVAL",
            "embeddingDimension": EMBEDDING_DIMENSION,
            "text": {
                "truncationMode": "END",
                "value": text
            }
        }
    }
    
    response = bedrock_client.invoke_model(
        modelId=EMBEDDING_MODEL_ID,
        body=json.dumps(request_body),
        contentType="application/json",
        accept="application/json"
    )
    
    response_body = json.loads(response['body'].read())
    return response_body['embeddings'][0]['embedding']


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
    Seed the Aurora PostgreSQL database with products and Nova Multimodal embeddings
    
    Requirements covered:
    - 2.7: Populate 30 products across 6 categories
    - 2.8: Generate 1024-dimensional embeddings using Amazon Nova Multimodal Embeddings
    """
    console.print("\n[bold blue]🌱 Seeding ClickShop Database[/bold blue]")
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
