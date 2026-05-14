"""
Chat API Router for Meridian.

Handles chat interactions with the AI shopping assistant across all three phases:
- Phase 1: Direct RDS Data API connection (simple SQL queries)
- Phase 2: Via MCP (awslabs.postgres-mcp-server) abstraction
- Phase 3: Hybrid search - Semantic (pgvector) + Lexical (tsvector/tsrank)
"""

import re
import uuid
from datetime import datetime
from typing import Literal, Optional, List, Any
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
    results_to_packages,
)
from backend.catalog_compat import row_to_api_product, rows_to_api_products

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
    phase: Literal[1, 2, 3, 4]
    customer_id: Optional[str] = None
    conversation_id: Optional[str] = None


class TraceTelemetry(BaseModel):
    """Optional rich telemetry for trace UI."""
    category: Optional[str] = None
    component: Optional[str] = None
    status: Optional[str] = None
    fields: Optional[List[dict]] = None
    memory: Optional[dict] = None
    tokens: Optional[dict] = None


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
    telemetry: Optional[TraceTelemetry] = None


class Product(BaseModel):
    """Trip package in API shape (legacy field names for frontend)."""
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


class MemoryFact(BaseModel):
    """Long-term preference fact from Aurora."""
    key: str
    value: str
    source: Optional[str] = None
    confidence: Optional[float] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    message: str
    products: Optional[List[Product]] = None
    order: Optional[Order] = None
    activities: List[ActivityEntry]
    follow_ups: Optional[List[str]] = None
    conversation_id: Optional[str] = None
    memory_facts: Optional[List[MemoryFact]] = None


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

    Phase 1 & 2: SQL filter search (trip_type, operator, price filters)
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

        category_keywords_map = {
            "City Breaks": "city breaks",
            "Beach & Resort": "beach resort",
            "Adventure & Outdoors": "adventure travel",
            "Wellness & Luxury": "wellness travel",
            "Family Trips": "family trips",
            "Business Travel": "business travel",
        }
        category_keyword = (
            category_keywords_map.get(primary_category, "travel packages")
            if primary_category
            else "travel packages"
        )

        if phase in [1, 2]:
            if prices:
                avg_price = sum(prices) / len(prices)
                if avg_price > 2000:
                    follow_ups.append(f"{category_keyword} under $2000")

            if brands:
                for brand in brands:
                    if brand.lower() not in query_lower:
                        follow_ups.append(f"{brand} {category_keyword}")
                        break

            if "City Breaks" in categories:
                follow_ups.append("Beach & Resort")
            elif "Beach & Resort" in categories:
                follow_ups.append("Adventure & Outdoors")
            elif "Adventure & Outdoors" in categories:
                follow_ups.append("Wellness & Luxury")
            else:
                follow_ups.append("Show me city breaks")

        else:
            semantic_suggestions = {
                "City Breaks": [
                    "Romantic weekend in Europe",
                    "Culture and food focused city trip",
                    "Walkable neighborhoods with great museums",
                ],
                "Beach & Resort": [
                    "All-inclusive beach escape",
                    "Snorkeling and calm waters",
                    "Luxury overwater villa",
                ],
                "Adventure & Outdoors": [
                    "Moderate hiking with guided tours",
                    "Northern lights season trip",
                    "Rainforest and wildlife experience",
                ],
                "Wellness & Luxury": [
                    "Spa retreat in the mountains",
                    "Fine dining and wine country",
                    "Traditional ryokan with onsen",
                ],
                "Family Trips": [
                    "Theme park vacation with kids",
                    "Beach resort with kids club",
                    "National park wildlife safari",
                ],
                "Business Travel": [
                    "Quick conference stopover",
                    "Hotel near airport with lounge",
                    "Flexible change policy",
                ],
            }

            if primary_category in semantic_suggestions:
                for suggestion in semantic_suggestions[primary_category]:
                    if suggestion.lower() not in query_lower:
                        follow_ups.append(suggestion)
                        if len(follow_ups) >= 2:
                            break

            if "City Breaks" not in categories:
                follow_ups.append("Weekend city break under $2k")
            elif "Beach & Resort" not in categories:
                follow_ups.append("Relaxing beach vacation")

    else:
        if phase in [1, 2]:
            follow_ups = [
                "City breaks",
                "Beach & Resort",
                "Business travel",
            ]
        else:
            follow_ups = [
                "Romantic week in Europe",
                "Family-friendly beach resort",
                "Adventure trip with guided hikes",
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
    Simple trip_type matching and LIKE queries.
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
    product_dicts = results_to_packages(results)
    products = [Product(**row_to_api_product(p)) for p in product_dicts]

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

    sql, display_sql, search_title = build_search_sql(params, limit)
    results: List[dict] = []
    used_mcp = False

    if MCP_AVAILABLE:
        activities.append(create_activity(
            activity_type="mcp",
            title="MCP: connect_to_database",
            details="Connecting to Aurora PostgreSQL via postgres-mcp-server",
            agent_name="Phase2Agent",
            agent_file="agents/phase2/agent.py"
        ))
        try:
            async with mcp_session() as client:
                results = await client.run_query(sql)
            used_mcp = True
            activities.append(create_activity(
                activity_type="mcp",
                title="MCP: run_query",
                details=f"Executing via MCP: {search_title}",
                sql_query=display_sql,
                agent_name="Phase2Agent",
                agent_file="agents/phase2/agent.py"
            ))
        except Exception as e:
            log_error("phase2_mcp_fallback", error=str(e))
            activities.append(create_activity(
                activity_type="error",
                title="MCP failed — falling back to RDS Data API",
                details=str(e),
                agent_name="Phase2Agent",
                agent_file="agents/phase2/agent.py"
            ))
    else:
        activities.append(create_activity(
            activity_type="database",
            title="MCP SDK unavailable — using RDS Data API",
            details="Install MCP dependencies to enable postgres-mcp-server",
            agent_name="Phase2Agent",
            agent_file="agents/phase2/agent.py"
        ))

    if not used_mcp:
        db = get_rds_data_client()
        results, display_sql, search_title = await execute_keyword_search(db, params, limit)
        activities.append(create_activity(
            activity_type="database",
            title=f"RDS Data API: {search_title}",
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

    product_dicts = results_to_packages(results)
    products = [Product(**row_to_api_product(p)) for p in product_dicts]

    return products, activities


# =============================================================================
# PHASE 3: Hybrid Search - Semantic (pgvector) + Lexical (tsvector/tsrank)
# Combines embedding similarity with PostgreSQL full-text search
# =============================================================================

async def phase3_lexical_search(query: str, limit: int = 5) -> tuple[List[Product], List[ActivityEntry]]:
    """Lexical-only fallback when Bedrock embeddings are unavailable."""
    activities = []
    start_time = datetime.utcnow()
    db = get_rds_data_client()

    activities.append(create_activity(
        activity_type="search",
        title="Lexical fallback (tsvector)",
        details="Embeddings unavailable — ranking with search_vector only",
        agent_name="SearchAgent",
        agent_file="agents/phase3/search_agent.py",
    ))

    sql = """
        SELECT package_id, name, operator, price_per_person, description,
               image_url, trip_type, durations,
               ts_rank(search_vector, plainto_tsquery('english', %s)) AS lexical_score
        FROM trip_packages
        WHERE search_vector @@ plainto_tsquery('english', %s)
        ORDER BY lexical_score DESC
        LIMIT %s
    """
    results = await db.execute(sql, (query, query, limit))
    search_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

    activities.append(create_activity(
        activity_type="search",
        title=f"Lexical search found {len(results)} packages",
        execution_time_ms=search_time,
        agent_name="SearchAgent",
        agent_file="agents/phase3/search_agent.py",
    ))

    products = [Product(**row_to_api_product(row)) for row in results]
    return products, activities


async def phase3_search(query: str, limit: int = 5) -> tuple[List[Product], List[ActivityEntry]]:
    """
    Phase 3: Hybrid search combining semantic and lexical approaches.
    - Semantic: Cohere Embed v4 embeddings with pgvector cosine similarity
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
        details="Cohere Embed v4 Embeddings (1024d)",
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
                    SELECT package_id, name, operator, price_per_person, description, 
                           image_url, trip_type, durations,
                           1 - (embedding <=> %s::vector) as semantic_score
                    FROM trip_packages
                    WHERE price_per_person <= %s
                ),
                lexical_search AS (
                    SELECT package_id,
                           ts_rank(
                               to_tsvector('english', name || ' ' || COALESCE(description, '') || ' ' || COALESCE(operator, '')),
                               plainto_tsquery('english', %s)
                           ) as lexical_score
                    FROM trip_packages
                    WHERE price_per_person <= %s
                )
                SELECT s.package_id, s.name, s.operator, s.price_per_person, s.description,
                       s.image_url, s.trip_type, s.durations,
                       s.semantic_score,
                       COALESCE(l.lexical_score, 0) as lexical_score,
                       (0.7 * s.semantic_score + 0.3 * COALESCE(l.lexical_score, 0)) as combined_score
                FROM semantic_search s
                LEFT JOIN lexical_search l ON s.package_id = l.package_id
                ORDER BY combined_score DESC
                LIMIT %s
            """
            results = await db.execute(sql, (embedding_str, price_filter, query, price_filter, limit))
        else:
            sql = """
                WITH semantic_search AS (
                    SELECT package_id, name, operator, price_per_person, description, 
                           image_url, trip_type, durations,
                           1 - (embedding <=> %s::vector) as semantic_score
                    FROM trip_packages
                ),
                lexical_search AS (
                    SELECT package_id,
                           ts_rank(
                               to_tsvector('english', name || ' ' || COALESCE(description, '') || ' ' || COALESCE(operator, '')),
                               plainto_tsquery('english', %s)
                           ) as lexical_score
                    FROM trip_packages
                )
                SELECT s.package_id, s.name, s.operator, s.price_per_person, s.description,
                       s.image_url, s.trip_type, s.durations,
                       s.semantic_score,
                       COALESCE(l.lexical_score, 0) as lexical_score,
                       (0.7 * s.semantic_score + 0.3 * COALESCE(l.lexical_score, 0)) as combined_score
                FROM semantic_search s
                LEFT JOIN lexical_search l ON s.package_id = l.package_id
                ORDER BY combined_score DESC
                LIMIT %s
            """
            results = await db.execute(sql, (embedding_str, query, limit))
        
        search_time = int((datetime.utcnow() - start_time).total_seconds() * 1000) - embedding_time

        # Build display SQL based on whether price filter was used
        if price_filter:
            display_sql = f"WITH semantic_search AS (SELECT ..., 1 - (embedding <=> query_vector) as score FROM trip_packages WHERE price_per_person <= {price_filter}), lexical_search AS (SELECT ..., ts_rank(...) FROM trip_packages) SELECT ... ORDER BY (0.7 * semantic + 0.3 * lexical) DESC LIMIT {limit}"
        else:
            display_sql = f"WITH semantic_search AS (SELECT ..., 1 - (embedding <=> query_vector) as score FROM trip_packages), lexical_search AS (SELECT ..., ts_rank(...) FROM trip_packages) SELECT ... ORDER BY (0.7 * semantic + 0.3 * lexical) DESC LIMIT {limit}"

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
        
        products = [Product(**row_to_api_product(row)) for row in results]
        
        return products, activities
        
    except Exception as e:
        activities.append(create_activity(
            activity_type="error",
            title="Hybrid search failed",
            details=str(e),
            agent_name="SearchAgent",
            agent_file="agents/phase3/search_agent.py"
        ))

        # Fallback to lexical search, then keyword search
        lexical_products, lexical_activities = await phase3_lexical_search(query, limit)
        activities.extend(lexical_activities)
        if lexical_products:
            return lexical_products, activities
        fallback_products, fallback_activities = await phase1_search(query, limit)
        activities.extend(fallback_activities)
        return fallback_products, activities


# =============================================================================
# PHASE 4: Strands ConciergeOrchestrator + MemoryAgent (@tool) + Aurora memory
# =============================================================================

def _memory_activity_to_entry(entry: Any) -> ActivityEntry:
    """Convert MemoryAgent/ConciergeOrchestrator activity to API ActivityEntry."""
    if isinstance(entry, ActivityEntry):
        return entry
    data = entry.model_dump() if hasattr(entry, "model_dump") else dict(entry)
    telemetry = data.pop("telemetry", None)
    return ActivityEntry(
        **data,
        telemetry=TraceTelemetry(**telemetry) if telemetry else None,
    )


async def phase4_search(
    query: str,
    customer_id: str,
    conversation_id: Optional[str] = None,
    limit: int = 5,
) -> tuple[List[Product], List[ActivityEntry], str, str, List[MemoryFact]]:
    """
    Phase 4: Recall Aurora memory via Strands @tool, hybrid search, persist turn.
    """
    from backend.agents.phase4.concierge import create_concierge
    from backend.memory.store import DEMO_TRAVELER_ID

    tid = customer_id or DEMO_TRAVELER_ID
    runtime = create_concierge()
    products, raw_activities, message, conv_id, facts = await runtime.process_turn(
        query,
        tid,
        conversation_id,
        limit,
        search_fn=phase3_search,
    )
    activities = [_memory_activity_to_entry(a) for a in raw_activities]
    memory_facts = [
        MemoryFact(
            key=f["key"],
            value=f["value"],
            source=f.get("source"),
            confidence=f.get("confidence"),
        )
        for f in facts
    ]
    return products, activities, message, conv_id, memory_facts


# =============================================================================
# PHASE 3: ProductAgent - Inventory and Product Details
# Handles stock checks and detailed product information
# =============================================================================

async def phase3_availability_check(query: str) -> tuple[List[Product], List[ActivityEntry], str]:
    """
    Phase 3: ProductAgent handles availability and stock queries.
    Supervisor delegates to ProductAgent for stock/availability questions.
    
    Returns: (products, activities, message)
    """
    activities = []
    start_time = datetime.utcnow()
    
    db = get_rds_data_client()
    
    # Step 0: Supervisor delegates to ProductAgent
    activities.append(create_activity(
        activity_type="reasoning",
        title="Delegating to ProductAgent",
        details="Supervisor routing availability request to specialized agent",
        agent_name="SupervisorAgent",
        agent_file="agents/phase3/supervisor.py"
    ))
    
    # Extract product name from query
    query_lower = query.lower()
    
    # Try to find the product mentioned
    activities.append(create_activity(
        activity_type="search",
        title="ProductAgent: Finding product",
        details="Searching for mentioned product",
        agent_name="ProductAgent",
        agent_file="agents/phase3/product_agent.py"
    ))
    
    # Search for the product by name similarity
    sql = """
        SELECT package_id, name, operator, price_per_person, description, 
               image_url, trip_type, durations, availability
        FROM trip_packages
        WHERE LOWER(name) LIKE %s OR LOWER(brand) LIKE %s
        LIMIT 1
    """
    
    # Extract key terms from query
    search_terms = []
    for word in query_lower.split():
        if word not in ['is', 'the', 'in', 'stock', 'available', 'do', 'you', 'have', 'check', 'what', 'sizes', 'for']:
            search_terms.append(word)
    
    results = []
    for term in search_terms:
        results = await db.execute(sql, (f'%{term}%', f'%{term}%'))
        if results:
            break
    
    search_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
    
    if not results:
        activities.append(create_activity(
            activity_type="result",
            title="ProductAgent: Product not found",
            execution_time_ms=search_time,
            agent_name="ProductAgent",
            agent_file="agents/phase3/product_agent.py"
        ))
        
        activities.append(create_activity(
            activity_type="result",
            title="ProductAgent returned to Supervisor",
            details="No matching product found",
            agent_name="SupervisorAgent",
            agent_file="agents/phase3/supervisor.py"
        ))
        
        return [], activities, "I couldn't find that specific product. Try searching for it by name or trip_type."
    
    product = results[0]
    availability = product.get('availability', {})
    
    # Check availability
    activities.append(create_activity(
        activity_type="availability",
        title=f"ProductAgent: Checking availability",
        details=f"Product: {product['name']}",
        sql_query="SELECT availability, durations FROM trip_packages WHERE package_id = ?",
        agent_name="ProductAgent",
        agent_file="agents/phase3/product_agent.py"
    ))
    
    # Calculate total stock
    if isinstance(availability, dict):
        if 'quantity' in availability:
            total_stock = availability['quantity']
        else:
            total_stock = sum(availability.values()) if availability else 0
    else:
        total_stock = 0
    
    availability_time = int((datetime.utcnow() - start_time).total_seconds() * 1000) - search_time
    
    activities.append(create_activity(
        activity_type="result",
        title=f"ProductAgent: Stock verified",
        details=f"Total: {total_stock} units available",
        execution_time_ms=availability_time,
        agent_name="ProductAgent",
        agent_file="agents/phase3/product_agent.py"
    ))
    
    # ProductAgent returns to Supervisor
    activities.append(create_activity(
        activity_type="result",
        title="ProductAgent returned to Supervisor",
        details=f"Inventory check complete for {product['name']}",
        agent_name="SupervisorAgent",
        agent_file="agents/phase3/supervisor.py"
    ))
    
    # Build response message
    durations = product.get('durations', [])
    if total_stock > 0:
        if durations:
            sizes_str = ', '.join(durations[:5])
            message = f"**{product['name']}** is in stock! We have {total_stock} units available in sizes: {sizes_str}."
        else:
            message = f"**{product['name']}** is in stock with {total_stock} units available."
    else:
        message = f"**{product['name']}** is currently out of stock. Would you like me to find similar alternatives?"
    
    # Return the product
    products = [Product(**row_to_api_product(product))]
    
    return products, activities, message


def is_availability_query(query: str) -> bool:
    """Check if the query is asking about availability/stock."""
    query_lower = query.lower()
    availability_patterns = [
        'in stock', 'available', 'do you have', 'check stock',
        'availability', 'how many', 'what sizes', 'size available',
        'is the', 'is there', 'got any'
    ]
    return any(pattern in query_lower for pattern in availability_patterns)


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process a chat message with the AI shopping assistant.
    
    Routes to appropriate search implementation based on phase:
    - Phase 1: Direct RDS Data API
    - Phase 2: Via MCP abstraction
    - Phase 3: Multi-agent orchestration
      - SearchAgent: Semantic search queries
      - ProductAgent: Inventory/stock queries
      - OrderAgent: Order processing (via /order endpoint)
    """
    activities = []

    # Phase 3/4: Check if this is an availability query -> route to ProductAgent
    if request.phase in (3, 4) and is_availability_query(request.message):
        activities.append(create_activity(
            activity_type="reasoning",
            title="Processing with Multi-Agent Orchestration",
            details=f"Query: {request.message[:80]}{'...' if len(request.message) > 80 else ''}",
            agent_name="SupervisorAgent",
            agent_file="agents/phase3/supervisor.py"
        ))
        
        try:
            products, availability_activities, message = await phase3_availability_check(request.message)
            activities.extend(availability_activities)
            
            follow_ups = ["Show me similar products", "What other sizes do you have?", "Find me alternatives"]
            
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
                title="ProductAgent error",
                details=str(e),
                agent_name="ProductAgent",
                agent_file="agents/phase3/product_agent.py"
            ))
            # Fall through to regular search

    # Phase 4: Strands ConciergeOrchestrator + Aurora memory (@tool)
    if request.phase == 4:
        from backend.memory.store import DEMO_TRAVELER_ID

        activities.append(create_activity(
            activity_type="reasoning",
            title="Processing with personal concierge (Strands + Aurora memory)",
            details=f"Query: {request.message[:80]}{'...' if len(request.message) > 80 else ''}",
            agent_name="ConciergeOrchestrator",
            agent_file="agents/phase4/concierge.py",
        ))
        try:
            products, search_activities, message, conv_id, memory_facts = await phase4_search(
                request.message,
                customer_id=request.customer_id or DEMO_TRAVELER_ID,
                conversation_id=request.conversation_id,
                limit=5,
            )
            activities.extend(search_activities)
            follow_ups = generate_follow_ups(request.message, products, request.phase)
            return ChatResponse(
                message=message,
                products=products if products else None,
                order=None,
                activities=activities,
                follow_ups=follow_ups,
                conversation_id=conv_id,
                memory_facts=memory_facts,
            )
        except Exception as e:
            log_error("phase4_search", error=str(e))
            activities.append(create_activity(
                activity_type="error",
                title="Concierge error",
                details=str(e),
                agent_name="ConciergeOrchestrator",
                agent_file="agents/phase4/concierge.py",
            ))
            return ChatResponse(
                message="I encountered an error loading memory. Please try again.",
                products=None,
                order=None,
                activities=activities,
                follow_ups=["Romantic week in Europe", "Family-friendly beach resort", "Tokyo culture trip"],
            )

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
            if request.phase in (3, 4):
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
                message = "No results found. Phase 1/2 uses keyword matching only. Try specific terms like 'running shoes' or 'Nike', or switch to Phase 3 for natural language search."
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
    Only available in Phase 3 which supports Cohere Embed v4 embeddings.
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
        # 1. Use Amazon Bedrock with Cohere Embed v4 Embeddings:
        #    bedrock = boto3.client('bedrock-runtime')
        #    response = bedrock.invoke_model(
        #        modelId='amazon.titan-embed-image-v1',
        #        body=json.dumps({'inputImage': base64_image})
        #    )
        #    image_embedding = json.loads(response['body'].read())['embedding']
        #
        # 2. Query products table using pgvector cosine similarity:
        #    SELECT ... FROM trip_packages
        #    ORDER BY embedding <=> %s::vector
        #    LIMIT 5
        #
        # 3. The embedding_service already supports generate_image_embedding()
        #    but requires base64 encoding of the uploaded image.
        sql = """
            SELECT package_id, name, operator, price_per_person, description, 
                   image_url, trip_type, durations
            FROM trip_packages
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
        
        products = [Product(**row_to_api_product(row)) for i, row in enumerate(results)]
        
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
    """Request model for booking processing."""
    product_id: str
    size: Optional[str] = None
    quantity: int = 1
    phase: Literal[1, 2, 3, 4]


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
        1: ("Phase1Agent", "agents/phase1/agent.py"),
        2: ("Phase2Agent", "agents/phase2/agent.py"),
        3: ("OrderAgent", "agents/phase3/order_agent.py"),
        4: ("OrderAgent", "agents/phase4/order_agent.py"),
    }
    agent_name, agent_file = phase_configs[request.phase]

    try:
        db = get_rds_data_client()

        # Step 1: Product lookup
        activities.append(create_activity(
            activity_type="search",
            title="Looking up product details",
            details=f"Package ID: {request.product_id}",
            agent_name=agent_name,
            agent_file=agent_file
        ))

        # Simulate processing time
        await asyncio.sleep(0.3)

        sql = """
            SELECT package_id, name, operator, price_per_person, description,
                   image_url, trip_type, durations
            FROM trip_packages
            WHERE package_id = %s
        """
        results = await db.execute(sql, (request.product_id,))

        if not results:
            activities.append(create_activity(
                activity_type="error",
                title="Product not found",
                details=f"No package with ID {request.product_id}",
                agent_name=agent_name,
                agent_file=agent_file
            ))
            return OrderResponse(
                message="Sorry, I couldn't find that product. It may no longer be available.",
                order=None,
                activities=activities
            )

        product = results[0]
        pkg = row_to_api_product(product)
        lookup_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        activities.append(create_activity(
            activity_type="result",
            title=f"Found: {pkg['name']}",
            details=f"${pkg['price']:.2f} pp — {pkg['brand']}",
            execution_time_ms=lookup_time,
            agent_name=agent_name,
            agent_file=agent_file
        ))

        # Step 2: Inventory check
        activities.append(create_activity(
            activity_type="availability",
            title="Checking availability",
            details=f"Size: {request.size or 'One Size'}, Qty: {request.quantity}",
            agent_name=agent_name,
            agent_file=agent_file
        ))

        await asyncio.sleep(0.2)

        # Mock availability check - always in stock for demo
        in_stock = True
        stock_qty = random.randint(5, 50)

        availability_time = int((datetime.utcnow() - start_time).total_seconds() * 1000) - lookup_time

        activities.append(create_activity(
            activity_type="availability",
            title="In Stock" if in_stock else "Out of Stock",
            details=f"{stock_qty} units available",
            execution_time_ms=availability_time,
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
        subtotal = pkg['price'] * request.quantity
        tax = round(subtotal * config.order.tax_rate, 2)
        shipping = 0.0 if subtotal >= config.order.free_shipping_threshold else config.order.shipping_fee
        total = round(subtotal + tax + shipping, 2)

        payment_time = int((datetime.utcnow() - start_time).total_seconds() * 1000) - lookup_time - availability_time

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
                    product_id=pkg['product_id'],
                    name=pkg['name'],
                    size=request.size,
                    quantity=request.quantity,
                    unit_price=pkg['price']
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

        message = f"Great choice! I've placed your booking for **{pkg['name']}**.\n\n" \
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
