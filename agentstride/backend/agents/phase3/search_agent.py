"""
Phase 3 Search Agent - Specialized in semantic and visual product search.

Implements semantic and visual search using:
- Amazon Nova Multimodal Embeddings (1024 dimensions)
- pgvector for similarity search
- RDS Data API for Aurora PostgreSQL access
- Claude Sonnet 4.5 via Amazon Bedrock (cross-region inference)

Requirements: 11.2, 11.6, 11.7, 11.8
"""

import os
import json
import uuid
from datetime import datetime
from typing import Callable, Any, Optional, List, Tuple

import boto3
from strands import Agent, tool
from strands.models import BedrockModel
from pydantic import BaseModel

from db.rds_data_client import get_rds_data_client


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


# Amazon Nova Multimodal Embeddings Configuration (1024 dimensions)
# Same model used for both text and image embeddings (cross-modal search)
EMBEDDING_MODEL_ID = os.getenv("EMBEDDING_MODEL", "amazon.nova-2-multimodal-embeddings-v1:0")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1024"))


class SearchAgent:
    """
    Search Agent specialized in semantic and visual product search.
    
    Requirements:
    - 11.2: Search_Agent specialized in semantic and visual product search
    - 11.6: Performs semantic search using Nova 2 Multimodal embeddings (3072 dims)
    - 11.7: Generates embedding from image using Nova 2 Multimodal for visual search
    - 11.8: Uses same vector space for text and image embeddings (cross-modal search)
    """
    
    def __init__(self, activity_callback: Optional[Callable[[ActivityEntry], Any]] = None):
        """
        Initialize Search agent.
        
        Args:
            activity_callback: Optional callback for reporting agent activities
        """
        self.activity_callback = activity_callback or (lambda x: None)
        self.db = get_rds_data_client()
        
        # Initialize Bedrock clients
        self.bedrock_runtime = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        )
        
        # Initialize model for agent (cross-region inference)
        self.model = BedrockModel(
            model_id="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
            region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        )
        
        # Create agent with search tools
        self.agent = Agent(
            model=self.model,
            tools=[self._semantic_search_tool, self._visual_search_tool],
            system_prompt=self._get_system_prompt()
        )
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the search agent."""
        return """You are a Search Agent specialized in finding products for customers.

Your capabilities:
- Semantic text search: Find products based on natural language descriptions
- Visual search: Find similar products based on uploaded images

You use Nova 2 Multimodal embeddings for both text and image search, enabling cross-modal search where text and images share the same vector space.

When searching:
- Understand the customer's intent
- Use semantic search for text queries
- Use visual search when an image is provided
- Return relevant products with similarity scores"""
    
    def _log_activity(
        self,
        activity_type: str,
        title: str,
        details: Optional[str] = None,
        sql_query: Optional[str] = None,
        execution_time_ms: Optional[int] = None
    ):
        """Log an activity entry."""
        entry = ActivityEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat() + "Z",
            activity_type=activity_type,
            title=title,
            details=details,
            sql_query=sql_query,
            execution_time_ms=execution_time_ms,
            agent_name="SearchAgent"
        )
        self.activity_callback(entry)
    
    def _generate_text_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using Amazon Nova Multimodal Embeddings.
        
        Requirement 11.6: Uses Nova Multimodal Embeddings (1024 dims)
        """
        request_body = {
            "schemaVersion": "nova-multimodal-embed-v1",
            "taskType": "SINGLE_EMBEDDING",
            "singleEmbeddingParams": {
                "embeddingPurpose": "TEXT_RETRIEVAL",
                "embeddingDimension": EMBEDDING_DIMENSION,
                "text": {
                    "truncationMode": "END",
                    "value": text
                }
            }
        }
        
        response = self.bedrock_runtime.invoke_model(
            modelId=EMBEDDING_MODEL_ID,
            body=json.dumps(request_body),
            contentType="application/json",
            accept="application/json"
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['embeddings'][0]['embedding']
    
    def _generate_image_embedding(self, image_bytes: bytes) -> List[float]:
        """
        Generate embedding for image using Amazon Nova Multimodal Embeddings.
        
        Requirement 11.7: Generates embedding from image for visual search
        Uses same Nova Multimodal model for cross-modal search (1024 dims)
        """
        import base64
        
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Use Nova Multimodal Embeddings for images (same model as text)
        request_body = {
            "schemaVersion": "nova-multimodal-embed-v1",
            "taskType": "SINGLE_EMBEDDING",
            "singleEmbeddingParams": {
                "embeddingPurpose": "IMAGE_RETRIEVAL",
                "embeddingDimension": EMBEDDING_DIMENSION,
                "image": {
                    "format": "jpeg",  # Will be auto-detected
                    "source": {
                        "bytes": image_base64
                    }
                }
            }
        }
        
        response = self.bedrock_runtime.invoke_model(
            modelId=EMBEDDING_MODEL_ID,
            body=json.dumps(request_body),
            contentType="application/json",
            accept="application/json"
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['embeddings'][0]['embedding']
    
    @tool
    async def _semantic_search_tool(self, query: str, limit: int = 5) -> List[dict]:
        """
        Search for products using semantic text search.
        
        Args:
            query: Natural language search query
            limit: Maximum number of results (default 5)
            
        Returns:
            List of products with similarity scores
        """
        return await self.semantic_search(query, limit)
    
    @tool
    async def _visual_search_tool(self, image_description: str) -> List[dict]:
        """
        Placeholder for visual search - actual image bytes handled separately.
        
        Args:
            image_description: Description of the image being searched
            
        Returns:
            Message indicating visual search requires image upload
        """
        return {"message": "Visual search requires an uploaded image. Please use the image upload endpoint."}
    
    async def semantic_search(self, query: str, limit: int = 5) -> dict:
        """
        Perform semantic product search using text embedding.
        
        Requirement 11.6: Semantic search using Nova Multimodal Embeddings (1024 dims)
        
        Args:
            query: Search query text
            limit: Maximum number of results
            
        Returns:
            Dict with products list and similarity scores
        """
        start_time = datetime.utcnow()
        
        # Generate query embedding
        self._log_activity(
            activity_type="embedding",
            title="Generating text embedding",
            details=f"Query: {query[:50]}..."
        )
        
        query_embedding = self._generate_text_embedding(query)
        
        embedding_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        self._log_activity(
            activity_type="embedding",
            title="Text embedding generated",
            details=f"Dimension: {len(query_embedding)}",
            execution_time_ms=embedding_time
        )
        
        # Search using semantic_product_search function
        search_start = datetime.utcnow()
        
        sql = """
            SELECT * FROM semantic_product_search(%s::vector, %s)
        """
        
        # Convert embedding to PostgreSQL vector format
        embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
        
        results = await self.db.execute(sql, (embedding_str, limit))
        
        search_time = int((datetime.utcnow() - search_start).total_seconds() * 1000)
        
        self._log_activity(
            activity_type="search",
            title=f"Semantic search: '{query}'",
            details=f"Found {len(results)} products",
            sql_query="SELECT * FROM semantic_product_search(...)",
            execution_time_ms=search_time
        )
        
        # Format results
        products = []
        for r in results:
            products.append({
                "product_id": r['product_id'],
                "name": r['name'],
                "brand": r['brand'],
                "price": float(r['price']),
                "description": r['description'],
                "image_url": r['image_url'],
                "category": r['category'],
                "similarity": float(r['similarity'])
            })
        
        return {"products": products, "query": query}
    
    async def visual_search(self, image_bytes: bytes, limit: int = 5) -> dict:
        """
        Perform visual product search using image embedding.
        
        Requirement 11.7: Visual search using Nova Multimodal image embeddings
        Requirement 11.8: Same vector space for cross-modal search (same model for text and images)
        
        Args:
            image_bytes: Image data as bytes
            limit: Maximum number of results
            
        Returns:
            Dict with products list and similarity scores
        """
        start_time = datetime.utcnow()
        
        # Generate image embedding
        self._log_activity(
            activity_type="embedding",
            title="Generating image embedding",
            details=f"Image size: {len(image_bytes)} bytes"
        )
        
        image_embedding = self._generate_image_embedding(image_bytes)
        
        embedding_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        self._log_activity(
            activity_type="embedding",
            title="Image embedding generated",
            details=f"Dimension: {len(image_embedding)}",
            execution_time_ms=embedding_time
        )
        
        # Search using semantic_product_search function (same as text - cross-modal)
        search_start = datetime.utcnow()
        
        sql = """
            SELECT * FROM semantic_product_search(%s::vector, %s)
        """
        
        embedding_str = '[' + ','.join(map(str, image_embedding)) + ']'
        
        results = await self.db.execute(sql, (embedding_str, limit))
        
        search_time = int((datetime.utcnow() - search_start).total_seconds() * 1000)
        
        self._log_activity(
            activity_type="search",
            title="Visual search completed",
            details=f"Found {len(results)} similar products",
            sql_query="SELECT * FROM semantic_product_search(...)",
            execution_time_ms=search_time
        )
        
        # Format results
        products = []
        for r in results:
            products.append({
                "product_id": r['product_id'],
                "name": r['name'],
                "brand": r['brand'],
                "price": float(r['price']),
                "description": r['description'],
                "image_url": r['image_url'],
                "category": r['category'],
                "similarity": float(r['similarity'])
            })
        
        return {"products": products, "search_type": "visual"}


def create_search_agent(
    activity_callback: Optional[Callable[[ActivityEntry], Any]] = None
) -> SearchAgent:
    """Create a Search agent instance."""
    return SearchAgent(activity_callback=activity_callback)
