"""
Embedding Service for Meridian.

Provides Cohere Embed v4 embeddings for semantic search.
Uses global.cohere.embed-v4 with 1024 dimensions.
"""

import os
import json
from typing import List, Optional
import boto3


class EmbeddingService:
    """
    Service for generating embeddings using Cohere Embed v4.

    Default is 1024 dimensions for best accuracy within HNSW index limits.
    """

    MODEL_ID = "global.cohere.embed-v4"
    DEFAULT_DIMENSIONS = 1024
    MAX_TEXT_LENGTH = 2048

    def __init__(self, region: Optional[str] = None, dimensions: Optional[int] = None):
        """
        Initialize embedding service.

        Args:
            region: AWS region (defaults to AWS_DEFAULT_REGION env var)
            dimensions: Embedding dimensions (default 1024)
        """
        self.region = region or os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.dimensions = dimensions or int(os.getenv("EMBEDDING_DIMENSION", self.DEFAULT_DIMENSIONS))
        self._bedrock_client = None

    @property
    def bedrock_client(self):
        """Get or create Bedrock runtime client."""
        if self._bedrock_client is None:
            self._bedrock_client = boto3.client(
                "bedrock-runtime",
                region_name=self.region
            )
        return self._bedrock_client

    def generate_text_embedding(self, text: str, input_type: str = "search_document") -> List[float]:
        """
        Generate embedding for text using Cohere Embed v4.

        Args:
            text: Input text (max 2048 tokens)
            input_type: "search_document" for indexing, "search_query" for queries

        Returns:
            1024-dimensional embedding vector
        """
        if len(text) > self.MAX_TEXT_LENGTH:
            text = text[:self.MAX_TEXT_LENGTH]

        request_body = {
            "texts": [text],
            "input_type": input_type,
            "embedding_types": ["float"],
            "truncate": "END"
        }

        response = self.bedrock_client.invoke_model(
            modelId=self.MODEL_ID,
            body=json.dumps(request_body),
            contentType="application/json",
            accept="application/json"
        )

        response_body = json.loads(response["body"].read())
        return response_body["embeddings"]["float"][0]


# Global service instance
_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Get or create the global embedding service instance."""
    global _service
    if _service is None:
        _service = EmbeddingService()
    return _service
