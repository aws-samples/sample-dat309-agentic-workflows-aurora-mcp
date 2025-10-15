from strands import tool
from lib.aurora_db import check_inventory

@tool
def check_product_inventory(product_id: str, size: str = None) -> dict:
    """Check if a product is available in the requested size."""
    # Query Aurora database for real-time inventory
    inventory = check_inventory(product_id, size)
    # Return availability status, quantity, and available sizes
    return inventory
