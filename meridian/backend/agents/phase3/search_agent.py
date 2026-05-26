"""
Phase 3 — Search Agent (Strands @tool + pgvector semantic search).

Presenter walkthrough
---------------------
Show `_semantic_search_tool` and `semantic_search()` when explaining
specialist agents under the Phase 3 supervisor. Uses EmbeddingService
(1024-dim Cohere Embed v4) to match Aurora's vector(1024) column.

AWS docs:
  - Cohere Embed v4 on Bedrock:
    https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-embed-v4.html
  - Aurora PostgreSQL pgvector:
    https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraPostgreSQL.Extensions.html#AuroraPostgreSQL.Extensions.pgvector
  - RDS Data API (hybrid SQL execution):
    https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/data-api.html

Requirements: 11.2, 11.6
"""

import os
import uuid
from datetime import datetime
from typing import Callable, Any, Optional, List

from strands import Agent, tool
from strands.models import BedrockModel

from backend.config import config
from pydantic import BaseModel

from backend.db.embedding_service import get_embedding_service
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
        self.embedding_service = get_embedding_service()

        self.model = BedrockModel(
            model_id=config.bedrock.model_id,
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
        
        query_embedding = self.embedding_service.generate_text_embedding(
            query, input_type="search_query"
        )

        embedding_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        self._log_activity(
            activity_type="embedding",
            title="Text embedding generated",
            details=f"Dimension: {len(query_embedding)} ({EMBEDDING_DIMENSION}d pgvector)",
            execution_time_ms=embedding_time
        )

        search_start = datetime.utcnow()

        sql = """
            SELECT * FROM semantic_trip_search(%s::vector, %s)
        """

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
