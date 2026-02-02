"""
Shared search utilities for AgentStride.

Provides common search logic used by Phase 1 and Phase 2 to eliminate code duplication.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from backend.config import config


@dataclass
class SearchParams:
    """Parsed search parameters from a query string."""
    query: str
    query_lower: str
    price_filter: Optional[float]
    matched_category: Optional[str]
    search_pattern: str


def parse_search_query(query: str) -> SearchParams:
    """
    Parse a search query to extract filters and patterns.

    Args:
        query: Raw search query string

    Returns:
        SearchParams with extracted filters
    """
    query_lower = query.lower()

    # Parse price filter
    price_filter = None
    price_match = re.search(r'(?:under|below|less than|<)\s*\$?(\d+(?:\.\d{2})?)', query_lower)
    if price_match:
        price_filter = float(price_match.group(1))

    # Match category from keywords
    matched_category = None
    for keyword, category in config.search.category_keywords.items():
        if keyword in query_lower:
            matched_category = category
            break

    # Build search pattern for LIKE queries
    search_pattern = f"%{query}%"

    return SearchParams(
        query=query,
        query_lower=query_lower,
        price_filter=price_filter,
        matched_category=matched_category,
        search_pattern=search_pattern,
    )


async def execute_keyword_search(
    db: Any,
    params: SearchParams,
    limit: int = 5
) -> Tuple[List[Dict], str, str]:
    """
    Execute a keyword-based search query.

    Args:
        db: Database client
        params: Parsed search parameters
        limit: Maximum results to return

    Returns:
        Tuple of (results, display_sql, search_title)
    """
    results = []
    display_sql = ""
    search_title = ""

    if params.matched_category:
        # Category-based search
        if params.price_filter:
            sql = """
                SELECT product_id, name, brand, price, description,
                       image_url, category, available_sizes
                FROM products
                WHERE category = %s AND price <= %s
                ORDER BY price ASC
                LIMIT %s
            """
            display_sql = f"SELECT ... FROM products WHERE category = '{params.matched_category}' AND price <= {params.price_filter} ORDER BY price ASC LIMIT {limit}"
            results = await db.execute(sql, (params.matched_category, params.price_filter, limit))
        else:
            sql = """
                SELECT product_id, name, brand, price, description,
                       image_url, category, available_sizes
                FROM products
                WHERE category = %s
                ORDER BY price ASC
                LIMIT %s
            """
            display_sql = f"SELECT ... FROM products WHERE category = '{params.matched_category}' ORDER BY price ASC LIMIT {limit}"
            results = await db.execute(sql, (params.matched_category, limit))

        search_title = f"Category filter: {params.matched_category}"

    elif params.query_lower in ["shoes", "sneakers"]:
        # Only match if query is exactly "shoes" or "sneakers"
        if params.price_filter:
            sql = """
                SELECT product_id, name, brand, price, description,
                       image_url, category, available_sizes
                FROM products
                WHERE category IN ('Running Shoes', 'Training Shoes') AND price <= %s
                ORDER BY price ASC
                LIMIT %s
            """
            display_sql = f"SELECT ... FROM products WHERE category IN ('Running Shoes', 'Training Shoes') AND price <= {params.price_filter} ORDER BY price ASC LIMIT {limit}"
            results = await db.execute(sql, (params.price_filter, limit))
        else:
            sql = """
                SELECT product_id, name, brand, price, description,
                       image_url, category, available_sizes
                FROM products
                WHERE category IN ('Running Shoes', 'Training Shoes')
                ORDER BY price ASC
                LIMIT %s
            """
            display_sql = f"SELECT ... FROM products WHERE category IN ('Running Shoes', 'Training Shoes') ORDER BY price ASC LIMIT {limit}"
            results = await db.execute(sql, (limit,))

        search_title = "Searching shoe categories"

    else:
        # ILIKE text search
        if params.price_filter:
            sql = """
                SELECT product_id, name, brand, price, description,
                       image_url, category, available_sizes
                FROM products
                WHERE (name ILIKE %s OR description ILIKE %s OR brand ILIKE %s)
                      AND price <= %s
                ORDER BY price ASC
                LIMIT %s
            """
            display_sql = f"SELECT ... FROM products WHERE (name ILIKE '%{params.query}%' OR description ILIKE ... OR brand ILIKE ...) AND price <= {params.price_filter} ORDER BY price ASC LIMIT {limit}"
            results = await db.execute(
                sql,
                (params.search_pattern, params.search_pattern, params.search_pattern, params.price_filter, limit)
            )
        else:
            sql = """
                SELECT product_id, name, brand, price, description,
                       image_url, category, available_sizes
                FROM products
                WHERE name ILIKE %s OR description ILIKE %s OR brand ILIKE %s
                ORDER BY price ASC
                LIMIT %s
            """
            display_sql = f"SELECT ... FROM products WHERE (name ILIKE '%{params.query}%' OR description ILIKE ... OR brand ILIKE ...) ORDER BY price ASC LIMIT {limit}"
            results = await db.execute(
                sql,
                (params.search_pattern, params.search_pattern, params.search_pattern, limit)
            )

        search_title = f"Text search: {params.query}"

    return results, display_sql, search_title


def build_search_sql(params: SearchParams, limit: int = 5) -> Tuple[str, str, str]:
    """
    Build SQL query string for search (used by MCP which takes raw SQL).

    Unlike execute_keyword_search which uses parameterized queries,
    this builds a complete SQL string for MCP's run_query tool.

    Args:
        params: Parsed search parameters
        limit: Maximum results to return

    Returns:
        Tuple of (full_sql, display_sql, search_title)
    """
    base_columns = """product_id, name, brand, price, description,
                      image_url, category, available_sizes"""

    if params.matched_category:
        # Category-based search
        if params.price_filter:
            sql = f"""
                SELECT {base_columns}
                FROM products
                WHERE category = '{params.matched_category}' AND price <= {params.price_filter}
                ORDER BY price ASC
                LIMIT {limit}
            """
            display_sql = f"SELECT ... FROM products WHERE category = '{params.matched_category}' AND price <= {params.price_filter} ORDER BY price ASC LIMIT {limit}"
        else:
            sql = f"""
                SELECT {base_columns}
                FROM products
                WHERE category = '{params.matched_category}'
                ORDER BY price ASC
                LIMIT {limit}
            """
            display_sql = f"SELECT ... FROM products WHERE category = '{params.matched_category}' ORDER BY price ASC LIMIT {limit}"

        search_title = f"Category filter: {params.matched_category}"

    elif "shoes" in params.query_lower or "sneakers" in params.query_lower:
        # Shoe categories search
        if params.price_filter:
            sql = f"""
                SELECT {base_columns}
                FROM products
                WHERE category IN ('Running Shoes', 'Training Shoes') AND price <= {params.price_filter}
                ORDER BY price ASC
                LIMIT {limit}
            """
            display_sql = f"SELECT ... FROM products WHERE category IN ('Running Shoes', 'Training Shoes') AND price <= {params.price_filter} ORDER BY price ASC LIMIT {limit}"
        else:
            sql = f"""
                SELECT {base_columns}
                FROM products
                WHERE category IN ('Running Shoes', 'Training Shoes')
                ORDER BY price ASC
                LIMIT {limit}
            """
            display_sql = f"SELECT ... FROM products WHERE category IN ('Running Shoes', 'Training Shoes') ORDER BY price ASC LIMIT {limit}"

        search_title = "Searching shoe categories"

    else:
        # ILIKE text search - escape single quotes in query
        safe_query = params.query.replace("'", "''")
        safe_pattern = f"%{safe_query}%"

        if params.price_filter:
            sql = f"""
                SELECT {base_columns}
                FROM products
                WHERE (name ILIKE '{safe_pattern}' OR description ILIKE '{safe_pattern}' OR brand ILIKE '{safe_pattern}')
                      AND price <= {params.price_filter}
                ORDER BY price ASC
                LIMIT {limit}
            """
            display_sql = f"SELECT ... FROM products WHERE (name ILIKE '%{params.query}%' OR ...) AND price <= {params.price_filter} ORDER BY price ASC LIMIT {limit}"
        else:
            sql = f"""
                SELECT {base_columns}
                FROM products
                WHERE name ILIKE '{safe_pattern}' OR description ILIKE '{safe_pattern}' OR brand ILIKE '{safe_pattern}'
                ORDER BY price ASC
                LIMIT {limit}
            """
            display_sql = f"SELECT ... FROM products WHERE (name ILIKE '%{params.query}%' OR ...) ORDER BY price ASC LIMIT {limit}"

        search_title = f"Text search: {params.query}"

    return sql.strip(), display_sql, search_title


def results_to_products(results: List[Dict]) -> List[Dict]:
    """
    Convert database results to product dictionaries.

    Args:
        results: Raw database results

    Returns:
        List of product dictionaries with proper types
    """
    return [
        {
            "product_id": row["product_id"],
            "name": row["name"],
            "brand": row["brand"] or "",
            "price": float(row["price"]),
            "description": row["description"] or "",
            "image_url": row["image_url"] or "",
            "category": row["category"],
            "available_sizes": row.get("available_sizes"),
        }
        for row in results
    ]
