"""
Embedding Tools for Meridian agents.

Provides Cohere Embed v4 embedding generation for text.
Uses global.cohere.embed-v4 via Amazon Bedrock (1024 dimensions).
"""

import os
import json
from typing import List

import boto3


# Cohere Embed v4 configuration
EMBEDDING_CONFIG = {
    "model_id": os.getenv("EMBEDDING_MODEL", "global.cohere.embed-v4"),
    "dimensions": int(os.getenv("EMBEDDING_DIMENSION", "1024")),
    "region": os.getenv("BEDROCK_REGION", "us-east-1"),
    "input_types": ["text"],
    "max_text_length": 2048,
}


def _get_bedrock_client():
    """Get Bedrock Runtime client."""
    return boto3.client(
        'bedrock-runtime',
        region_name=EMBEDDING_CONFIG["region"]
    )


async def generate_text_embedding(text: str, input_type: str = "search_document") -> List[float]:
    """
    Generate embedding for text using Cohere Embed v4.

    Args:
        text: Input text (max 2048 tokens)
        input_type: "search_document" for indexing, "search_query" for queries

    Returns:
        1024-dimensional embedding vector
    """
    client = _get_bedrock_client()

    request_body = {
        "texts": [text],
        "input_type": input_type,
        "embedding_types": ["float"],
        "truncate": "END"
    }

    response = client.invoke_model(
        modelId=EMBEDDING_CONFIG["model_id"],
        body=json.dumps(request_body),
        contentType="application/json",
        accept="application/json"
    )

    response_body = json.loads(response['body'].read())
    return response_body['embeddings']['float'][0]
