"""
Phase 3 Search Agent - Specialized in semantic trip package search.

Implements semantic search using:
- Cohere Embed v4 (1024 dimensions)
- pgvector for similarity search
- RDS Data API for Aurora PostgreSQL access
- Claude Opus 4.7 via Amazon Bedrock (cross-region inference)

Requirements: 11.2, 11.6
"""

import os
import json
import uuid
from datetime import datetime
from typing import Callable, Any, Optional, List

import boto3
from strands import Agent, tool
from strands.models import BedrockModel
from pydantic import BaseModel

from backend.db.rds_data_client import get_rds_data_client


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


# Cohere Embed v4 Configuration (1024 dimensions)
EMBEDDING_MODEL_ID = os.getenv("EMBEDDING_MODEL", "cohere.embed-v4:0")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1024"))


class SearchAgent:
    """
    Search Agent specialized in semantic trip package search.

    Requirements:
    - 11.2: Search_Agent specialized in semantic product search
    - 11.6: Performs semantic search using Cohere Embed v4 (1024 dims)
    """

    def __init__(self, activity_callback: Optional[Callable[[ActivityEntry], Any]] = None):
        self.activity_callback = activity_callback or (lambda x: None)
        self.db = get_rds_data_client()

        self.bedrock_runtime = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        )

        self.model = BedrockModel(
            model_id="global.anthropic.claude-opus-4-7-v1",
            region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        )

        self.agent = Agent(
            model=self.model,
            tools=[self._semantic_search_tool],
            system_prompt=self._get_system_prompt()
        )

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the search agent."""
        return """You are a Search Agent specialized in finding trip packages for travelers.

Your capabilities:
- Semantic text search over the trip catalog using natural language

You use Cohere Embed v4 embeddings with pgvector for high-quality semantic search.

When searching:
- Understand the traveler's intent (destination, vibe, party size hints)
- Use semantic search for open-ended trip discovery
- Return relevant packages with similarity scores"""

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

    def _generate_text_embedding(self, text: str, input_type: str = "search_query") -> List[float]:
        """Generate embedding for text using Cohere Embed v4."""
        request_body = {
            "texts": [text],
            "input_type": input_type,
            "embedding_types": ["float"],
            "truncate": "END"
        }

        response = self.bedrock_runtime.invoke_model(
            modelId=EMBEDDING_MODEL_ID,
            body=json.dumps(request_body),
            contentType="application/json",
            accept="application/json"
        )

        response_body = json.loads(response['body'].read())
        return response_body['embeddings']['float'][0]

    @tool
    async def _semantic_search_tool(self, query: str, limit: int = 5) -> List[dict]:
        """
        Search for trip packages using semantic text search.

        Args:
            query: Natural language search query
            limit: Maximum number of results (default 5)

        Returns:
            List of products with similarity scores
        """
        return await self.semantic_search(query, limit)

    async def semantic_search(self, query: str, limit: int = 5) -> dict:
        """
        Perform semantic trip search using text embedding.
        
        Requirement 11.6: Semantic search using Cohere Embed v4 (1024 dims)
        
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
            SELECT * FROM semantic_trip_search(%s::vector, %s)
        """
        
        # Convert embedding to PostgreSQL vector format
        embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
        
        results = await self.db.execute(sql, (embedding_str, limit))
        
        search_time = int((datetime.utcnow() - search_start).total_seconds() * 1000)
        
        self._log_activity(
            activity_type="search",
            title=f"Semantic search: '{query}'",
            details=f"Found {len(results)} packages",
            sql_query="SELECT * FROM semantic_trip_search(...)",
            execution_time_ms=search_time
        )
        
        # Format results
        packages = []
        for r in results:
            packages.append({
                "package_id": r['package_id'],
                "name": r['name'],
                "operator": r['operator'],
                "price_per_person": float(r['price_per_person']),
                "description": r['description'],
                "image_url": r['image_url'],
                "trip_type": r['trip_type'],
                "destination": r.get('destination'),
                "similarity": float(r['similarity'])
            })

        return {"packages": packages, "query": query}
    


def create_search_agent(
    activity_callback: Optional[Callable[[ActivityEntry], Any]] = None
) -> SearchAgent:
    """Create a Search agent instance."""
    return SearchAgent(activity_callback=activity_callback)
