"""
Embedding Service for ClickShop.

Provides Nova Multimodal Embeddings for semantic search.
Uses amazon.nova-2-multimodal-embeddings-v1:0 with 1024 dimensions.
"""

import os
import json
from typing import List, Optional
import boto3


class EmbeddingService:
    """
    Service for generating embeddings using Amazon Nova Multimodal Embeddings.
    
    Supports text and image embeddings with configurable dimensions (256, 384, 1024, 3072).
    Default is 1024 dimensions for best accuracy within HNSW index limits.
    """
    
    # Nova Multimodal Embeddings configuration
    MODEL_ID = "amazon.nova-2-multimodal-embeddings-v1:0"
    DEFAULT_DIMENSIONS = 1024
    SUPPORTED_DIMENSIONS = [256, 384, 1024, 3072]
    MAX_TEXT_LENGTH = 8192  # 8K tokens
    
    def __init__(self, region: Optional[str] = None, dimensions: Optional[int] = None):
        """
        Initialize embedding service.
        
        Args:
            region: AWS region (defaults to AWS_DEFAULT_REGION env var)
            dimensions: Embedding dimensions (256, 384, 1024, or 3072)
        """
        self.region = region or os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.dimensions = dimensions or int(os.getenv("EMBEDDING_DIMENSION", self.DEFAULT_DIMENSIONS))
        
        if self.dimensions not in self.SUPPORTED_DIMENSIONS:
            raise ValueError(f"Dimensions must be one of {self.SUPPORTED_DIMENSIONS}")
        
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
    
    def generate_text_embedding(self, text: str, normalize: bool = True) -> List[float]:
        """
        Generate embedding for text using Nova Multimodal Embeddings.
        
        Args:
            text: Input text (max 8K tokens)
            normalize: Whether to normalize the embedding vector (ignored for Nova)
            
        Returns:
            Embedding vector of configured dimensions
        """
        if len(text) > self.MAX_TEXT_LENGTH:
            text = text[:self.MAX_TEXT_LENGTH]  # Truncate if too long
        
        request_body = {
            "schemaVersion": "nova-multimodal-embed-v1",
            "taskType": "SINGLE_EMBEDDING",
            "singleEmbeddingParams": {
                "embeddingPurpose": "TEXT_RETRIEVAL",
                "embeddingDimension": self.dimensions,
                "text": {
                    "truncationMode": "END",
                    "value": text
                }
            }
        }
        
        response = self.bedrock_client.invoke_model(
            modelId=self.MODEL_ID,
            body=json.dumps(request_body),
            contentType="application/json",
            accept="application/json"
        )
        
        response_body = json.loads(response["body"].read())
        return response_body["embeddings"][0]["embedding"]


# Global service instance
_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Get or create the global embedding service instance."""
    global _service
    if _service is None:
        _service = EmbeddingService()
    return _service
