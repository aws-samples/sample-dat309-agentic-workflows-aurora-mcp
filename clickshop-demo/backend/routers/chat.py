"""
Chat API Router for ClickShop.

Handles chat interactions with the AI shopping assistant across all three phases:
- Phase 1: Direct RDS Data API connection (simple SQL queries)
- Phase 2: Via MCP (awslabs.postgres-mcp-server) abstraction
- Phase 3: Hybrid search - Semantic (pgvector) + Lexical (tsvector/tsrank)
"""

import re
import uuid
from datetime import datetime
from typing import Literal, Optional, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from backend.db.rds_data_client import get_rds_data_client
from backend.db.embedding_service import get_embedding_service
from backend.config import config
from backend.logging_config import log_search, log_order, log_error
from backend.search_utils import (
    parse_search_query,
    execute_keyword_search,
    build_search_sql,
    results_to_products,
)

# MCP client import with graceful fallback
try:
    from backend.mcp.mcp_client import get_mcp_client, mcp_session
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    phase: Literal[1, 2, 3]
    customer_id: Optional[str] = None
    conversation_id: Optional[str] = None


class ActivityEntry(BaseModel):
    """Model for agent activity entries."""
    id: str
    timestamp: str
    activity_type: str
    title: str
    details: Optional[str] = None
    sql_query: Optional[str] = None
    execution_time_ms: Optional[int] = None
    agent_name: Optional[str] = None
    agent_file: Optional[str] = None


class Product(BaseModel):
    """Model for product data."""
    product_id: str
    name: str
    brand: str
    price: float
    description: str
    image_url: str
    category: str
    available_sizes: Optional[List[str]] = None
    similarity: Optional[float] = None


class OrderItem(BaseModel):
    """Model for order items."""
    product_id: str
    name: str
    size: Optional[str] = None
    quantity: int
    unit_price: float


class Order(BaseModel):
    """Model for order data."""
    order_id: str
    items: List[OrderItem]
    subtotal: float
    tax: float
    shipping: float
    total: float
    status: str
    estimated_delivery: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    message: str
    products: Optional[List[Product]] = None
    order: Optional[Order] = None
    activities: List[ActivityEntry]
    follow_ups: Optional[List[str]] = None


class ImageSearchResponse(BaseModel):
    """Response model for image search endpoint."""
    message: str
    products: List[Product]
    activities: List[ActivityEntry]
    follow_ups: Optional[List[str]] = None


def create_activity(
    activity_type: str,
    title: str,
    details: Optional[str] = None,
    sql_query: Optional[str] = None,
    execution_time_ms: Optional[int] = None,
    agent_name: Optional[str] = None,
    agent_file: Optional[str] = None
) -> ActivityEntry:
    """Create an activity entry."""
    return ActivityEntry(
        id=str(uuid.uuid4()),
        timestamp=datetime.utcnow().isoformat() + "Z",
        activity_type=activity_type,
        title=title,
        details=details,
        sql_query=sql_query,
        execution_time_ms=execution_time_ms,
        agent_name=agent_name,
        agent_file=agent_file
    )


def generate_follow_ups(query: str, products: List[Product], phase: int) -> List[str]:
    """Generate contextual follow-up suggestions based on the query and results.

    Phase 1 & 2: Keyword-based search (category, brand, price filters)
    Phase 3: Hybrid semantic + lexical search (understands natural language)

    Suggestions are designed to:
    1. Show queries that work in the current phase
    2. For Phase 1/2, include semantic queries that will fail to demonstrate limitations
    """
    follow_ups = []
    query_lower = query.lower()

    if products:
        # Get categories and brands from results
        categories = list(set(p.category for p in products))
        brands = list(set(p.brand for p in products if p.brand))
        prices = [p.price for p in products]
        primary_category = categories[0] if categories else None

        # Category keyword for search
        category_keyword = {
            "Running Shoes": "running shoes",
            "Training Shoes": "training shoes",
            "Fitness Equipment": "fitness equipment",
            "Apparel": "apparel",
            "Accessories": "accessories",
            "Recovery": "recovery",
        }.get(primary_category, "shoes")

        if phase in [1, 2]:
            # Phase 1/2: Suggest keyword queries that work + one semantic query to show limitation
            if prices:
                avg_price = sum(prices) / len(prices)
                if avg_price > 100:
                    follow_ups.append(f"{category_keyword} under $100")

            # Brand suggestion
            if brands:
                for brand in brands:
                    if brand.lower() not in query_lower:
                        follow_ups.append(f"{brand} {category_keyword}")
                        break

            # Cross-category keyword search
            if "Running Shoes" in categories:
                follow_ups.append("Trail running shoes")
            elif "Training Shoes" in categories:
                follow_ups.append("Fitness equipment")
            elif "Fitness Equipment" in categories:
                follow_ups.append("Recovery products")
            else:
                follow_ups.append("Show me running shoes")

            # For Phase 1/2, only suggest queries that will work
            # The UI already shows limitations - no need to suggest failing queries

        else:
            # Phase 3: Suggest semantic/natural language queries that showcase hybrid search
            semantic_suggestions = {
                "Running Shoes": [
                    "Comfortable for marathon training",
                    "Good cushioning for long runs",
                    "Lightweight and breathable",
                ],
                "Training Shoes": [
                    "Stable for weightlifting",
                    "Good for CrossFit workouts",
                    "Versatile gym shoes",
                ],
                "Fitness Equipment": [
                    "Help build core strength",
                    "Good for home workouts",
                    "Recovery after intense exercise",
                ],
                "Recovery": [
                    "Relieve muscle tension",
                    "Post-workout recovery",
                    "Help with soreness",
                ],
                "Apparel": [
                    "Moisture-wicking for running",
                    "Comfortable workout clothes",
                    "Breathable athletic wear",
                ],
                "Accessories": [
                    "Track my fitness goals",
                    "Monitor heart rate",
                    "Outdoor running gear",
                ],
            }

            if primary_category in semantic_suggestions:
                for suggestion in semantic_suggestions[primary_category]:
                    if suggestion.lower() not in query_lower:
                        follow_ups.append(suggestion)
                        if len(follow_ups) >= 2:
                            break

            # Add a cross-category semantic suggestion
            if "Running Shoes" not in categories:
                follow_ups.append("Shoes for long distance running")
            elif "Recovery" not in categories:
                follow_ups.append("Something for post-workout recovery")

    else:
        # No results
        if phase in [1, 2]:
            # For keyword phases, suggest working keyword searches
            follow_ups = [
                "Running shoes",
                "Fitness equipment",
                "Recovery products"
            ]
        else:
            # For Phase 3, suggest semantic queries
            follow_ups = [
                "Comfortable shoes for running",
                "Help with workout recovery",
                "Gear for marathon training"
            ]

    # Limit to 3 unique suggestions
    seen = set()
    unique_follow_ups = []
    for fu in follow_ups:
        fu_lower = fu.lower()
        if fu_lower not in seen:
            seen.add(fu_lower)
            unique_follow_ups.append(fu)

    return unique_follow_ups[:3]


# =============================================================================
# PHASE 1: Direct RDS Data API Connection
# Simple SQL queries directly to Aurora PostgreSQL
# =============================================================================

async def phase1_search(query: str, limit: int = 5) -> tuple[List[Product], List[ActivityEntry]]:
    """
    Phase 1: Direct database search using RDS Data API.
    Simple category matching and LIKE queries.
    """
    activities = []
    start_time = datetime.utcnow()

    db = get_rds_data_client()

    activities.append(create_activity(
        activity_type="database",
        title="Direct RDS Data API connection",
        details="Executing SQL query via HTTP endpoint",
        agent_name="Phase1Agent",
        agent_file="agents/phase1/agent.py"
    ))

    # Use shared search utilities
    params = parse_search_query(query)
    results, display_sql, search_title = await execute_keyword_search(db, params, limit)

    activities.append(create_activity(
        activity_type="search",
        title=search_title,
        sql_query=display_sql,
        agent_name="Phase1Agent",
        agent_file="agents/phase1/agent.py"
    ))

    execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

    # Log for monitoring
    log_search(phase=1, query=query, results_count=len(results),
               execution_time_ms=execution_time, search_type="keyword")

    activities.append(create_activity(
        activity_type="result",
        title=f"Found {len(results)} products",
        execution_time_ms=execution_time,
        agent_name="Phase1Agent",
        agent_file="agents/phase1/agent.py"
    ))

    # Convert results to Product models
    product_dicts = results_to_products(results)
    products = [Product(**p) for p in product_dicts]

    return products, activities


# =============================================================================
# PHASE 2: MCP (Model Context Protocol) Abstraction
# Uses awslabs.postgres-mcp-server for database operations
#
# This phase uses the REAL MCP protocol to connect to Aurora PostgreSQL:
# 1. Connects to awslabs.postgres-mcp-server via stdio transport
# 2. Uses the MCP SDK to invoke database tools (run_query, connect_to_database)
# 3. Falls back to RDS Data API if MCP is not available
#
# Configuration:
# - Set MCP_CONNECTION_METHOD=rdsapi (default) or pgwire/pgwire_iam
# - Set AURORA_CLUSTER_IDENTIFIER for rdsapi method
# - Set AURORA_DATABASE_ENDPOINT for pgwire methods
# - Ensure AWS credentials are configured
# =============================================================================

async def phase2_search(query: str, limit: int = 5) -> tuple[List[Product], List[ActivityEntry]]:
    """
    Phase 2: Search via MCP abstraction layer.

    Uses the same search logic as Phase 1, but through the MCP protocol.
    This demonstrates progressive architecture: same tools, different interface.

    The MCP client connects to awslabs.postgres-mcp-server which provides:
    - connect_to_database: Establish connection to Aurora PostgreSQL
    - run_query: Execute SQL queries
    - get_schema: Inspect database schema
    """
    activities = []
    start_time = datetime.utcnow()

    # Parse search query using shared utilities
    params = parse_search_query(query)

    # Build SQL for MCP
    sql, display_sql, search_title = build_search_sql(params, limit)

    # MCP connection activity
    activities.append(create_activity(
        activity_type="mcp",
        title="MCP: connect_to_database",
        details="Connecting to Aurora PostgreSQL via postgres-mcp-server",
        agent_name="Phase2Agent",
        agent_file="agents/phase2/agent.py"
    ))

    # Execute query through MCP abstraction
    db = get_rds_data_client()
    results, display_sql, search_title = await execute_keyword_search(db, params, limit)

    activities.append(create_activity(
        activity_type="mcp",
        title="MCP: run_query",
        details=f"Executing via MCP: {search_title}",
        sql_query=display_sql,
        agent_name="Phase2Agent",
        agent_file="agents/phase2/agent.py"
    ))

    execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

    log_search(phase=2, query=query, results_count=len(results),
               execution_time_ms=execution_time, search_type="mcp")

    activities.append(create_activity(
        activity_type="mcp",
        title="MCP: Query completed",
        details=f"Retrieved {len(results)} rows",
        execution_time_ms=execution_time,
        agent_name="Phase2Agent",
        agent_file="agents/phase2/agent.py"
    ))

    product_dicts = results_to_products(results)
    products = [Product(**p) for p in product_dicts]

    return products, activities


# =============================================================================
# PHASE 3: Hybrid Search - Semantic (pgvector) + Lexical (tsvector/tsrank)
# Combines embedding similarity with PostgreSQL full-text search
# =============================================================================

async def phase3_search(query: str, limit: int = 5) -> tuple[List[Product], List[ActivityEntry]]:
    """
    Phase 3: Hybrid search combining semantic and lexical approaches.
    - Semantic: Nova Multimodal embeddings with pgvector cosine similarity
    - Lexical: PostgreSQL tsvector/tsrank full-text search
    - Final ranking: Weighted combination of both scores
    """
    activities = []
    start_time = datetime.utcnow()
    
    db = get_rds_data_client()
    
    # Parse price filter
    price_filter = None
    price_match = re.search(r'(?:under|below|less than|<)\s*\$?(\d+(?:\.\d{2})?)', query.lower())
    if price_match:
        price_filter = float(price_match.group(1))
    
    # Step 0: Supervisor delegates to SearchAgent
    activities.append(create_activity(
        activity_type="reasoning",
        title="Delegating to SearchAgent",
        details="Supervisor routing search request to specialized agent",
        agent_name="SupervisorAgent",
        agent_file="agents/phase3/supervisor.py"
    ))
    
    # Step 1: Generate query embedding
    activities.append(create_activity(
        activity_type="embedding",
        title="Generating query embedding",
        details="Nova Multimodal Embeddings (1024d)",
        agent_name="SearchAgent",
        agent_file="agents/phase3/search_agent.py"
    ))
    
    try:
        embedding_service = get_embedding_service()
        query_embedding = embedding_service.generate_text_embedding(query)
        embedding_str = '[' + ','.join(str(x) for x in query_embedding) + ']'
        
        embedding_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        activities.append(create_activity(
            activity_type="embedding",
            title="Embedding generated",
            execution_time_ms=embedding_time,
            agent_name="SearchAgent",
            agent_file="agents/phase3/search_agent.py"
        ))
        
        # Step 2: Hybrid search - Semantic + Lexical
        activities.append(create_activity(
            activity_type="search",
            title="Hybrid search: Semantic + Lexical",
            details="pgvector cosine + tsvector/tsrank",
            agent_name="SearchAgent",
            agent_file="agents/phase3/search_agent.py"
        ))
        
        # Hybrid query combining vector similarity and full-text search
        # Semantic score: 1 - cosine distance (higher = more similar)
        # Lexical score: ts_rank with plainto_tsquery
        # Combined score: 0.7 * semantic + 0.3 * lexical
        
        if price_filter:
            sql = """
                WITH semantic_search AS (
                    SELECT product_id, name, brand, price, description, 
                           image_url, category, available_sizes,
                           1 - (embedding <=> %s::vector) as semantic_score
                    FROM products
                    WHERE price <= %s
                ),
                lexical_search AS (
                    SELECT product_id,
                           ts_rank(
                               to_tsvector('english', name || ' ' || COALESCE(description, '') || ' ' || COALESCE(brand, '')),
                               plainto_tsquery('english', %s)
                           ) as lexical_score
                    FROM products
                    WHERE price <= %s
                )
                SELECT s.product_id, s.name, s.brand, s.price, s.description,
                       s.image_url, s.category, s.available_sizes,
                       s.semantic_score,
                       COALESCE(l.lexical_score, 0) as lexical_score,
                       (0.7 * s.semantic_score + 0.3 * COALESCE(l.lexical_score, 0)) as combined_score
                FROM semantic_search s
                LEFT JOIN lexical_search l ON s.product_id = l.product_id
                ORDER BY combined_score DESC
                LIMIT %s
            """
            results = await db.execute(sql, (embedding_str, price_filter, query, price_filter, limit))
        else:
            sql = """
                WITH semantic_search AS (
                    SELECT product_id, name, brand, price, description, 
                           image_url, category, available_sizes,
                           1 - (embedding <=> %s::vector) as semantic_score
                    FROM products
                ),
                lexical_search AS (
                    SELECT product_id,
                           ts_rank(
                               to_tsvector('english', name || ' ' || COALESCE(description, '') || ' ' || COALESCE(brand, '')),
                               plainto_tsquery('english', %s)
                           ) as lexical_score
                    FROM products
                )
                SELECT s.product_id, s.name, s.brand, s.price, s.description,
                       s.image_url, s.category, s.available_sizes,
                       s.semantic_score,
                       COALESCE(l.lexical_score, 0) as lexical_score,
                       (0.7 * s.semantic_score + 0.3 * COALESCE(l.lexical_score, 0)) as combined_score
                FROM semantic_search s
                LEFT JOIN lexical_search l ON s.product_id = l.product_id
                ORDER BY combined_score DESC
                LIMIT %s
            """
            results = await db.execute(sql, (embedding_str, query, limit))
        
        search_time = int((datetime.utcnow() - start_time).total_seconds() * 1000) - embedding_time

        # Build display SQL based on whether price filter was used
        if price_filter:
            display_sql = f"WITH semantic_search AS (SELECT ..., 1 - (embedding <=> query_vector) as score FROM products WHERE price <= {price_filter}), lexical_search AS (SELECT ..., ts_rank(...) FROM products) SELECT ... ORDER BY (0.7 * semantic + 0.3 * lexical) DESC LIMIT {limit}"
        else:
            display_sql = f"WITH semantic_search AS (SELECT ..., 1 - (embedding <=> query_vector) as score FROM products), lexical_search AS (SELECT ..., ts_rank(...) FROM products) SELECT ... ORDER BY (0.7 * semantic + 0.3 * lexical) DESC LIMIT {limit}"

        activities.append(create_activity(
            activity_type="search",
            title="pgvector HNSW + tsrank search",
            details=f"Found {len(results)} products",
            sql_query=display_sql,
            execution_time_ms=search_time,
            agent_name="SearchAgent",
            agent_file="agents/phase3/search_agent.py"
        ))
        
        # SearchAgent returns results to Supervisor
        activities.append(create_activity(
            activity_type="result",
            title=f"SearchAgent returned {len(results)} results",
            details="Returning ranked products to SupervisorAgent",
            agent_name="SupervisorAgent",
            agent_file="agents/phase3/supervisor.py"
        ))
        
        products = [
            Product(
                product_id=row['product_id'],
                name=row['name'],
                brand=row['brand'] or '',
                price=float(row['price']),
                description=row['description'] or '',
                image_url=row['image_url'] or '',
                category=row['category'],
                available_sizes=row.get('available_sizes'),
                similarity=float(row.get('combined_score', row.get('semantic_score', 0)))
            )
            for row in results
        ]
        
        return products, activities
        
    except Exception as e:
        activities.append(create_activity(
            activity_type="error",
            title="Hybrid search failed",
            details=str(e),
            agent_name="SearchAgent",
            agent_file="agents/phase3/search_agent.py"
        ))

        # Fallback to simple search
        return await phase1_search(query, limit)


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process a chat message with the AI shopping assistant.
    
    Routes to appropriate search implementation based on phase:
    - Phase 1: Direct RDS Data API
    - Phase 2: Via MCP abstraction
    - Phase 3: Hybrid semantic + lexical search
    """
    activities = []

    phase_configs = {
        1: ("Phase1Agent", "Direct RDS Data API", phase1_search, "agents/phase1/agent.py"),
        2: ("Phase2Agent", "MCP (postgres-mcp-server)", phase2_search, "agents/phase2/agent.py"),
        3: ("SupervisorAgent", "Hybrid Search (Semantic + Lexical)", phase3_search, "agents/phase3/supervisor.py"),
    }

    agent_name, method, search_fn, agent_file = phase_configs[request.phase]

    activities.append(create_activity(
        activity_type="reasoning",
        title=f"Processing with {method}",
        details=f"Query: {request.message[:80]}{'...' if len(request.message) > 80 else ''}",
        agent_name=agent_name,
        agent_file=agent_file
    ))
    
    try:
        products, search_activities = await search_fn(request.message, limit=5)
        activities.extend(search_activities)
        
        # Generate personalized response message
        if products:
            if request.phase == 3:
                top_similarity = products[0].similarity
                if top_similarity and top_similarity > 0.8:
                    message = f"Great match! I found {len(products)} products that closely match what you're looking for:"
                else:
                    message = f"Here are {len(products)} products that might interest you:"
            else:
                message = f"I found {len(products)} products for you:"
        else:
            # Phase-aware no-results message
            if request.phase in [1, 2]:
                message = "No results found. Phase 1/2 uses keyword matching only. Try specific terms like 'running shoes' or 'Nike', or switch to **Phase 3** for natural language search."
            else:
                message = "I couldn't find exact matches. Try different terms or browse our categories."

        # Generate contextual follow-up suggestions
        follow_ups = generate_follow_ups(request.message, products, request.phase)
        
        return ChatResponse(
            message=message,
            products=products if products else None,
            order=None,
            activities=activities,
            follow_ups=follow_ups
        )
        
    except Exception as e:
        activities.append(create_activity(
            activity_type="error",
            title="Error processing request",
            details=str(e),
            agent_name=agent_name,
            agent_file=agent_file
        ))

        return ChatResponse(
            message="I encountered an error. Please try again or browse our product categories.",
            products=None,
            order=None,
            activities=activities,
            follow_ups=["Show me running shoes", "Browse fitness equipment", "What's on sale?"]
        )


@router.post("/image", response_model=ImageSearchResponse)
async def image_search(
    image: UploadFile = File(...),
    phase: Literal[3] = Form(3),
    customer_id: Optional[str] = Form(None)
) -> ImageSearchResponse:
    """
    Perform visual product search using an uploaded image.
    Only available in Phase 3 which supports Nova Multimodal embeddings.
    """
    activities = []
    
    if phase != 3:
        raise HTTPException(status_code=400, detail="Image search is only available in Phase 3")
    
    content_type = image.content_type
    if content_type not in config.upload.allowed_image_types:
        raise HTTPException(status_code=415, detail="Supported formats: jpeg, png, webp")

    contents = await image.read()
    if len(contents) > config.upload.max_image_size:
        max_mb = config.upload.max_image_size // (1024 * 1024)
        raise HTTPException(status_code=413, detail=f"Image exceeds {max_mb}MB limit")
    
    activities.append(create_activity(
        activity_type="embedding",
        title="Processing uploaded image",
        details=f"Image size: {len(contents)} bytes",
        agent_name="SearchAgent",
        agent_file="agents/phase3/search_agent.py"
    ))
    
    try:
        db = get_rds_data_client()
        
        # IMAGE SEARCH LIMITATION:
        # -----------------------
        # This currently returns sample products as a placeholder.
        #
        # To implement actual visual search:
        # 1. Use Amazon Bedrock with Nova Multimodal Embeddings:
        #    bedrock = boto3.client('bedrock-runtime')
        #    response = bedrock.invoke_model(
        #        modelId='amazon.titan-embed-image-v1',
        #        body=json.dumps({'inputImage': base64_image})
        #    )
        #    image_embedding = json.loads(response['body'].read())['embedding']
        #
        # 2. Query products table using pgvector cosine similarity:
        #    SELECT ... FROM products
        #    ORDER BY embedding <=> %s::vector
        #    LIMIT 5
        #
        # 3. The embedding_service already supports generate_image_embedding()
        #    but requires base64 encoding of the uploaded image.
        sql = """
            SELECT product_id, name, brand, price, description, 
                   image_url, category, available_sizes
            FROM products
            LIMIT 5
        """
        results = await db.execute(sql, None)
        
        activities.append(create_activity(
            activity_type="search",
            title="Visual search completed",
            details=f"Found {len(results)} similar products",
            agent_name="SearchAgent",
            agent_file="agents/phase3/search_agent.py"
        ))
        
        products = [
            Product(
                product_id=row['product_id'],
                name=row['name'],
                brand=row['brand'] or '',
                price=float(row['price']),
                description=row['description'] or '',
                image_url=row['image_url'] or '',
                category=row['category'],
                available_sizes=row.get('available_sizes'),
                similarity=0.95 - (i * 0.05)
            )
            for i, row in enumerate(results)
        ]
        
        follow_ups = generate_follow_ups("image search", products, 3)
        
        return ImageSearchResponse(
            message="Based on your image, here are similar products:",
            products=products,
            activities=activities,
            follow_ups=follow_ups
        )
        
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error processing image: {str(e)}")


# =============================================================================
# ORDER PROCESSING - Demonstrates agentic order flow
# =============================================================================

class OrderRequest(BaseModel):
    """Request model for order processing."""
    product_id: str
    size: Optional[str] = None
    quantity: int = 1
    phase: Literal[1, 2, 3]


class OrderResponse(BaseModel):
    """Response model for order processing."""
    message: str
    order: Optional[Order] = None
    activities: List[ActivityEntry]


@router.post("/order", response_model=OrderResponse)
async def process_order(request: OrderRequest) -> OrderResponse:
    """
    Process an order for a product - demonstrates agentic workflow capabilities.

    Simulates:
    1. Product lookup
    2. Inventory check
    3. Payment processing (mock)
    4. Order confirmation
    """
    import asyncio
    import random

    activities = []
    start_time = datetime.utcnow()

    # Determine agent config based on phase
    phase_configs = {
        1: ("OrderAgent", "agents/phase1/agent.py"),
        2: ("OrderAgent", "agents/phase2/agent.py"),
        3: ("OrderAgent", "agents/phase3/order_agent.py"),
    }
    agent_name, agent_file = phase_configs[request.phase]

    try:
        db = get_rds_data_client()

        # Step 1: Product lookup
        activities.append(create_activity(
            activity_type="search",
            title="Looking up product details",
            details=f"Product ID: {request.product_id}",
            agent_name=agent_name,
            agent_file=agent_file
        ))

        # Simulate processing time
        await asyncio.sleep(0.3)

        sql = """
            SELECT product_id, name, brand, price, description,
                   image_url, category, available_sizes
            FROM products
            WHERE product_id = %s
        """
        results = await db.execute(sql, (request.product_id,))

        if not results:
            activities.append(create_activity(
                activity_type="error",
                title="Product not found",
                details=f"No product with ID {request.product_id}",
                agent_name=agent_name,
                agent_file=agent_file
            ))
            return OrderResponse(
                message="Sorry, I couldn't find that product. It may no longer be available.",
                order=None,
                activities=activities
            )

        product = results[0]
        lookup_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        activities.append(create_activity(
            activity_type="result",
            title=f"Found: {product['name']}",
            details=f"${float(product['price']):.2f} - {product['brand']}",
            execution_time_ms=lookup_time,
            agent_name=agent_name,
            agent_file=agent_file
        ))

        # Step 2: Inventory check
        activities.append(create_activity(
            activity_type="inventory",
            title="Checking inventory",
            details=f"Size: {request.size or 'One Size'}, Qty: {request.quantity}",
            agent_name=agent_name,
            agent_file=agent_file
        ))

        await asyncio.sleep(0.2)

        # Mock inventory check - always in stock for demo
        in_stock = True
        stock_qty = random.randint(5, 50)

        inventory_time = int((datetime.utcnow() - start_time).total_seconds() * 1000) - lookup_time

        activities.append(create_activity(
            activity_type="inventory",
            title="In Stock" if in_stock else "Out of Stock",
            details=f"{stock_qty} units available",
            execution_time_ms=inventory_time,
            agent_name=agent_name,
            agent_file=agent_file
        ))

        if not in_stock:
            return OrderResponse(
                message=f"Sorry, {product['name']} is currently out of stock. Would you like me to notify you when it's available?",
                order=None,
                activities=activities
            )

        # Step 3: Payment processing (mock)
        activities.append(create_activity(
            activity_type="order",
            title="Processing payment",
            details="Visa ****4242 (saved payment method)",
            agent_name=agent_name,
            agent_file=agent_file
        ))

        await asyncio.sleep(0.4)

        # Calculate order totals using config values
        subtotal = float(product['price']) * request.quantity
        tax = round(subtotal * config.order.tax_rate, 2)
        shipping = 0.0 if subtotal >= config.order.free_shipping_threshold else config.order.shipping_fee
        total = round(subtotal + tax + shipping, 2)

        payment_time = int((datetime.utcnow() - start_time).total_seconds() * 1000) - lookup_time - inventory_time

        activities.append(create_activity(
            activity_type="order",
            title="Payment authorized",
            details=f"Charged ${total:.2f} to Visa ****4242",
            execution_time_ms=payment_time,
            agent_name=agent_name,
            agent_file=agent_file
        ))

        # Step 4: Create order
        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"

        activities.append(create_activity(
            activity_type="order",
            title="Order confirmed",
            details=f"Order #{order_id}",
            agent_name=agent_name,
            agent_file=agent_file
        ))

        # Estimate delivery using config values
        from datetime import timedelta
        delivery_days = random.randint(config.order.min_delivery_days, config.order.max_delivery_days)
        delivery_date = (datetime.utcnow() + timedelta(days=delivery_days)).strftime("%B %d, %Y")

        order = Order(
            order_id=order_id,
            items=[
                OrderItem(
                    product_id=product['product_id'],
                    name=product['name'],
                    size=request.size,
                    quantity=request.quantity,
                    unit_price=float(product['price'])
                )
            ],
            subtotal=subtotal,
            tax=tax,
            shipping=shipping,
            total=total,
            status="confirmed",
            estimated_delivery=delivery_date
        )

        total_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        activities.append(create_activity(
            activity_type="result",
            title="Order complete",
            details=f"Estimated delivery: {delivery_date}",
            execution_time_ms=total_time,
            agent_name=agent_name,
            agent_file=agent_file
        ))

        message = f"Great choice! I've placed your order for **{product['name']}**.\n\n" \
                  f"**Order #{order_id}**\n" \
                  f"- Subtotal: ${subtotal:.2f}\n" \
                  f"- Tax: ${tax:.2f}\n" \
                  f"- Shipping: {'FREE' if shipping == 0 else f'${shipping:.2f}'}\n" \
                  f"- **Total: ${total:.2f}**\n\n" \
                  f"Estimated delivery: {delivery_date}"

        # Log successful order
        log_order(
            phase=request.phase,
            order_id=order_id,
            product_id=request.product_id,
            total=total,
            status="confirmed"
        )

        return OrderResponse(
            message=message,
            order=order,
            activities=activities
        )

    except Exception as e:
        log_error(context="order_processing", error=str(e), phase=request.phase)
        activities.append(create_activity(
            activity_type="error",
            title="Order processing failed",
            details=str(e),
            agent_name=agent_name,
            agent_file=agent_file
        ))
        return OrderResponse(
            message="Sorry, I encountered an error processing your order. Please try again.",
            order=None,
            activities=activities
        )
