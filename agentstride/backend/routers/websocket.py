"""
WebSocket Router for AgentStride.

Handles real-time activity streaming to the frontend.
"""

from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import json
import asyncio

router = APIRouter(tags=["websocket"])


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


class ActivityMessage(BaseModel):
    """WebSocket message for activity updates."""
    type: str = "activity"
    entry: ActivityEntry


class ConnectionManager:
    """Manages WebSocket connections for activity streaming."""
    
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)
    
    async def send_activity(self, entry: ActivityEntry):
        """Send an activity entry to all connected clients."""
        message = ActivityMessage(entry=entry)
        await self.broadcast(message.model_dump())


# Global connection manager instance
manager = ConnectionManager()


@router.websocket("/ws/activity")
async def activity_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for streaming agent activity updates.
    
    Clients connect to receive real-time updates about agent actions,
    SQL queries, and execution metrics.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle any incoming messages
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0  # Heartbeat timeout
                )
                # Handle ping/pong for connection keepalive
                if data == "ping":
                    await websocket.send_text("pong")
            except asyncio.TimeoutError:
                # Send heartbeat
                await websocket.send_text("heartbeat")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)


def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager instance."""
    return manager
