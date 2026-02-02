"""
API Routers for AgentStride Backend.

Contains route handlers for:
- chat: Chat endpoints for agent interactions
- products: Product catalog endpoints
- websocket: WebSocket activity streaming
"""

from .chat import router as chat_router
from .products import router as products_router
from .websocket import router as websocket_router

__all__ = ["chat_router", "products_router", "websocket_router"]
