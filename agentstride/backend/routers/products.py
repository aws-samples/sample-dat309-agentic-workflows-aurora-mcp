"""
Products API Router for ClickShop.

Handles product catalog retrieval using RDS Data API.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.db.rds_data_client import get_rds_data_client

router = APIRouter(prefix="/api/products", tags=["products"])


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


class ProductListResponse(BaseModel):
    """Response model for product list endpoint."""
    products: List[Product]
    total: int


@router.get("", response_model=ProductListResponse)
async def get_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of products to return"),
    offset: int = Query(0, ge=0, description="Number of products to skip"),
    featured: bool = Query(False, description="Get one product per category (featured)")
) -> ProductListResponse:
    """
    Retrieve the product catalog.
    
    Args:
        category: Optional category filter
        limit: Maximum number of products to return (default 50, max 100)
        offset: Number of products to skip for pagination
        featured: If true, returns one product per category
        
    Returns:
        ProductListResponse with list of products and total count
    """
    try:
        db = get_rds_data_client()
        
        # Featured mode: get one product per category
        if featured:
            query = """
                SELECT DISTINCT ON (category) 
                    product_id, name, brand, price, description, 
                    image_url, category, available_sizes
                FROM products
                ORDER BY category, price DESC
            """
            params = None
            
            results = await db.execute(query, params)
            
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
            
            return ProductListResponse(products=products, total=len(products))
        
        # Build query
        if category:
            query = """
                SELECT product_id, name, brand, price, description, 
                       image_url, category, available_sizes
                FROM products
                WHERE category = %s
                ORDER BY name
                LIMIT %s OFFSET %s
            """
            params = (category, limit, offset)
            
            count_query = "SELECT COUNT(*) as count FROM products WHERE category = %s"
            count_params = (category,)
        else:
            query = """
                SELECT product_id, name, brand, price, description, 
                       image_url, category, available_sizes
                FROM products
                ORDER BY name
                LIMIT %s OFFSET %s
            """
            params = (limit, offset)
            
            count_query = "SELECT COUNT(*) as count FROM products"
            count_params = None
        
        # Execute queries
        results = await db.execute(query, params)
        count_result = await db.execute_one(count_query, count_params)
        total = count_result['count'] if count_result else 0
        
        # Convert to Product models
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
        
        return ProductListResponse(products=products, total=total)
        
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database temporarily unavailable: {str(e)}"
        )


@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str) -> Product:
    """
    Retrieve a single product by ID.
    
    Args:
        product_id: The product identifier
        
    Returns:
        Product details
    """
    try:
        db = get_rds_data_client()
        
        query = """
            SELECT product_id, name, brand, price, description, 
                   image_url, category, available_sizes
            FROM products
            WHERE product_id = %s
        """
        
        result = await db.execute_one(query, (product_id,))
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Product {product_id} not found"
            )
        
        return Product(
            product_id=result['product_id'],
            name=result['name'],
            brand=result['brand'] or '',
            price=float(result['price']),
            description=result['description'] or '',
            image_url=result['image_url'] or '',
            category=result['category'],
            available_sizes=result.get('available_sizes')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database temporarily unavailable: {str(e)}"
        )
