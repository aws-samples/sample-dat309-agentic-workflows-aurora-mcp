"""
ClickShop Backend - FastAPI Application

Main entry point for the ClickShop demo backend server.
Provides REST API endpoints for chat interactions, product catalog,
and WebSocket streaming for real-time agent activity updates.

Requirements: 8.1
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()

# Import routers
from backend.routers import chat_router, products_router, websocket_router


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str
    version: str
    environment: str


class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str
    request_id: str | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    
    Handles startup and shutdown events for the FastAPI application.
    """
    # Startup
    print("Starting ClickShop Backend...")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"AWS Region: {os.getenv('AWS_DEFAULT_REGION', 'us-east-1')}")
    
    yield
    
    # Shutdown
    print("Shutting down ClickShop Backend...")


# Create FastAPI application
app = FastAPI(
    title="ClickShop Backend",
    description="Backend API for the ClickShop live-streaming shopping demo",
    version="1.0.0",
    lifespan=lifespan,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
        503: {"model": ErrorResponse, "description": "Service Unavailable"},
    }
)

# Configure CORS for frontend communication
# Allow requests from common frontend development ports
cors_origins = [
    "http://localhost:3000",      # React default
    "http://localhost:5173",      # Vite default
    "http://localhost:5174",      # Vite alternate
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]

# Add any custom origins from environment
custom_origins = os.getenv("CORS_ORIGINS", "")
if custom_origins:
    cors_origins.extend([origin.strip() for origin in custom_origins.split(",")])

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router)
app.include_router(products_router)
app.include_router(websocket_router)


@app.get("/", response_model=HealthResponse)
async def root() -> HealthResponse:
    """
    Root endpoint - returns basic service information.
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        environment=os.getenv("ENVIRONMENT", "development")
    )


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        HealthResponse with service status, version, and environment
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        environment=os.getenv("ENVIRONMENT", "development")
    )


@app.get("/api/health", response_model=HealthResponse)
async def api_health_check() -> HealthResponse:
    """
    API health check endpoint.
    
    Returns:
        HealthResponse with service status, version, and environment
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        environment=os.getenv("ENVIRONMENT", "development")
    )


# Exception handlers for consistent error responses
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions with consistent error format."""
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle unexpected exceptions with consistent error format."""
    from fastapi.responses import JSONResponse
    import uuid
    
    request_id = str(uuid.uuid4())
    print(f"Unexpected error (request_id={request_id}): {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "request_id": request_id
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("ENVIRONMENT", "development") == "development"
    
    print(f"Starting server on {host}:{port}")
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload
    )
