"""
Chat API Router for ClickShop.

Handles chat interactions with the AI shopping assistant across all three phases.
"""

import uuid
from datetime import datetime
from typing import Literal, Optional, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from backend.db.rds_data_client import get_rds_data_client

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


class ImageSearchResponse(BaseModel):
    """Response model for image search endpoint."""
    message: str
    products: List[Product]
    activities: List[ActivityEntry]


def create_activity(
    activity_type: str,
    title: str,
    details: Optional[str] = None,
    sql_query: Optional[str] = None,
    execution_time_ms: Optional[int] = None,
    agent_name: Optional[str] = None
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
        agent_name=agent_name
    )


async def simple_product_search(query: str, phase: int, limit: int = 5) -> tuple[List[Product], List[ActivityEntry]]:
    """
    Product search based on phase.
    
    Phase 1/2: Category-based or keyword matching (simpler approach)
    Phase 3: Would use semantic search with embeddings
    """
    activities = []
    start_time = datetime.utcnow()
    
    db = get_rds_data_client()
    
    # Check if query matches a category
    categories = ["Running Shoes", "Training Shoes", "Fitness Equipment", "Apparel", "Accessories", "Recovery"]
    query_lower = query.lower()
    
    matched_category = None
    for cat in categories:
        if cat.lower() in query_lower or query_lower in cat.lower():
            matched_category = cat
            break
    
    if matched_category:
        activities.append(create_activity(
            activity_type="search",
            title=f"Category search: {matched_category}",
            agent_name=f"Phase{phase}Agent"
        ))
        
        sql = """
            SELECT product_id, name, brand, price, description, 
                   image_url, category, available_sizes
            FROM products
            WHERE category = %s
            LIMIT %s
        """
        results = await db.execute(sql, (matched_category, limit))
    else:
        # For Phase 3, this would be semantic search
        # For Phase 1/2, we do a simple keyword match on name/description
        activities.append(create_activity(
            activity_type="search",
            title=f"Searching products for: {query}",
            agent_name=f"Phase{phase}Agent"
        ))
        
        # Get all products and filter in Python (RDS Data API ILIKE can be tricky)
        sql = """
            SELECT product_id, name, brand, price, description, 
                   image_url, category, available_sizes
            FROM products
            LIMIT 50
        """
        all_results = await db.execute(sql, None)
        
        # Filter by keyword match
        results = []
        for row in all_results:
            name = (row.get('name') or '').lower()
            desc = (row.get('description') or '').lower()
            brand = (row.get('brand') or '').lower()
            
            if query_lower in name or query_lower in desc or query_lower in brand:
                results.append(row)
                if len(results) >= limit:
                    break
    
    execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
    
    activities.append(create_activity(
        activity_type="search",
        title=f"Found {len(results)} products",
        sql_query="SELECT ... FROM products ...",
        execution_time_ms=execution_time,
        agent_name=f"Phase{phase}Agent"
    ))
    
    products = []
    for row in results:
        products.append(Product(
            product_id=row['product_id'],
            name=row['name'],
            brand=row['brand'] or '',
            price=float(row['price']),
            description=row['description'] or '',
            image_url=row['image_url'] or '',
            category=row['category'],
            available_sizes=row.get('available_sizes')
        ))
    
    return products, activities


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process a chat message with the AI shopping assistant.
    
    Args:
        request: Chat request containing message, phase, and optional customer/conversation IDs
        
    Returns:
        ChatResponse with agent message, optional products/order, and activity log
    """
    activities = []
    
    # Log the incoming request
    phase_names = {1: "Phase1Agent", 2: "Phase2Agent", 3: "SupervisorAgent"}
    agent_name = phase_names.get(request.phase, "Agent")
    
    activities.append(create_activity(
        activity_type="search",
        title=f"Processing message in Phase {request.phase}",
        details=f"Message: {request.message[:100]}...",
        agent_name=agent_name
    ))
    
    try:
        # Route to appropriate search based on phase
        products, search_activities = await simple_product_search(request.message, request.phase)
        activities.extend(search_activities)
        
        if products:
            message = f"I found {len(products)} products that might interest you:"
        else:
            message = "I couldn't find any products matching your request. Could you try a different search term?"
        
        return ChatResponse(
            message=message,
            products=products if products else None,
            order=None,
            activities=activities
        )
        
    except Exception as e:
        activities.append(create_activity(
            activity_type="error",
            title="Error processing request",
            details=str(e),
            agent_name=agent_name
        ))
        
        return ChatResponse(
            message=f"I encountered an error while processing your request. Please try again.",
            products=None,
            order=None,
            activities=activities
        )


@router.post("/image", response_model=ImageSearchResponse)
async def image_search(
    image: UploadFile = File(...),
    phase: Literal[3] = Form(3),
    customer_id: Optional[str] = Form(None)
) -> ImageSearchResponse:
    """
    Perform visual product search using an uploaded image.
    
    Only available in Phase 3 which supports Titan Multimodal embeddings.
    
    Args:
        image: Uploaded image file (jpeg, png, webp)
        phase: Must be 3 for image search
        customer_id: Optional customer identifier
        
    Returns:
        ImageSearchResponse with similar products and activity log
    """
    activities = []
    
    # Validate phase
    if phase != 3:
        raise HTTPException(
            status_code=400,
            detail="Image search is only available in Phase 3"
        )
    
    # Validate image format
    content_type = image.content_type
    if content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(
            status_code=415,
            detail="Supported formats: jpeg, png, webp"
        )
    
    # Check file size (5MB limit)
    contents = await image.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Image exceeds 5MB limit"
        )
    
    activities.append(create_activity(
        activity_type="embedding",
        title="Processing uploaded image",
        details=f"Image size: {len(contents)} bytes",
        agent_name="SearchAgent"
    ))
    
    try:
        # For now, return a sample of products as a placeholder
        # Full implementation would use Titan Multimodal embeddings
        db = get_rds_data_client()
        
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
            agent_name="SearchAgent"
        ))
        
        products = []
        for i, row in enumerate(results):
            products.append(Product(
                product_id=row['product_id'],
                name=row['name'],
                brand=row['brand'] or '',
                price=float(row['price']),
                description=row['description'] or '',
                image_url=row['image_url'] or '',
                category=row['category'],
                available_sizes=row.get('available_sizes'),
                similarity=0.95 - (i * 0.05)  # Simulated similarity scores
            ))
        
        return ImageSearchResponse(
            message="Based on your image, here are similar products:",
            products=products,
            activities=activities
        )
        
    except Exception as e:
        activities.append(create_activity(
            activity_type="error",
            title="Error processing image",
            details=str(e),
            agent_name="SearchAgent"
        ))
        
        raise HTTPException(
            status_code=503,
            detail=f"Error processing image: {str(e)}"
        )
