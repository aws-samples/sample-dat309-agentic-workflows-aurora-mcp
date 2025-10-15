from strands import tool
from lib.aurora_db import check_inventory

@tool
def check_product_inventory(product_id: str, size: str = None) -> dict:
    """Check if a product is available in the requested size."""
    
    inventory = check_inventory(product_id, size)
    
    return inventory
