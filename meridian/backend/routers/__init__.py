"""
API Routers for Meridian Backend.

Contains route handlers for:
- chat: Chat endpoints for agent interactions
- products: Product catalog endpoints
- websocket: WebSocket activity streaming
"""

from .chat import router as chat_router
from .products import router as packages_router, legacy_router as products_router
from .websocket import router as websocket_router
from .memory import router as memory_router

__all__ = ["chat_router", "products_router", "packages_router", "websocket_router", "memory_router"]
