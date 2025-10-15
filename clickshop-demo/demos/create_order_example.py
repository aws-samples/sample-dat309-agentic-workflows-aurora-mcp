from strands import tool

@tool
def create_order(product_id: str, customer_id: str, size: str, total_amount: float) -> dict:
    """Create order for customer."""
    # Generate unique order ID
    order_id = f"ORD-{int(time.time())}-{customer_id[:4]}"
    # Return order confirmation
    return {"order_id": order_id, "status": "confirmed", "total": total_amount}
