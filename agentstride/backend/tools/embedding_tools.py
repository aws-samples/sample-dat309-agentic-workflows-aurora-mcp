"""
Embedding Tools for ClickShop agents.

Provides Amazon Nova Multimodal embedding generation for text and images.
Uses the same model for both modalities enabling cross-modal search.

Model: amazon.nova-embed-multimodal-v1:0 (1024 dimensions)
"""

import os
import json
import base64
from typing import List

import boto3


# Amazon Nova Multimodal Embeddings configuration
EMBEDDING_CONFIG = {
    "model_id": os.getenv("EMBEDDING_MODEL", "amazon.nova-2-multimodal-embeddings-v1:0"),
    "dimensions": int(os.getenv("EMBEDDING_DIMENSION", "1024")),
    "region": os.getenv("BEDROCK_REGION", "us-east-1"),
    "input_types": ["text", "image"],
    "max_text_length": 8192,
    "supported_image_formats": ["jpeg", "png", "webp", "gif"],
    "max_image_size_mb": 5,
    "schema_version": "nova-multimodal-embed-v1"
}


def _get_bedrock_client():
    """Get Bedrock Runtime client."""
    return boto3.client(
        'bedrock-runtime',
        region_name=EMBEDDING_CONFIG["region"]
    )


async def generate_text_embedding(text: str) -> List[float]:
    """
    Generate embedding for text using Amazon Nova Multimodal Embeddings.
    
    Args:
        text: Input text (max 8192 characters)
        
    Returns:
        1024-dimensional embedding vector
    """
    client = _get_bedrock_client()
    
    request_body = {
        "schemaVersion": EMBEDDING_CONFIG["schema_version"],
        "taskType": "SINGLE_EMBEDDING",
        "singleEmbeddingParams": {
            "embeddingPurpose": "TEXT_RETRIEVAL",
            "embeddingDimension": EMBEDDING_CONFIG["dimensions"],
            "text": {
                "truncationMode": "END",
                "value": text
            }
        }
    }
    
    response = client.invoke_model(
        modelId=EMBEDDING_CONFIG["model_id"],
        body=json.dumps(request_body),
        contentType="application/json",
        accept="application/json"
    )
    
    response_body = json.loads(response['body'].read())
    return response_body['embeddings'][0]['embedding']


async def generate_image_embedding(image_bytes: bytes) -> List[float]:
    """
    Generate embedding for image using Amazon Nova Multimodal Embeddings.
    
    Uses the same model as text embeddings for cross-modal search capability.
    
    Args:
        image_bytes: Image data as bytes (jpeg, png, webp, or gif, max 5MB)
        
    Returns:
        1024-dimensional embedding vector
    """
    client = _get_bedrock_client()
    
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    request_body = {
        "schemaVersion": EMBEDDING_CONFIG["schema_version"],
        "taskType": "SINGLE_EMBEDDING",
        "singleEmbeddingParams": {
            "embeddingPurpose": "IMAGE_RETRIEVAL",
            "embeddingDimension": EMBEDDING_CONFIG["dimensions"],
            "image": {
                "format": "jpeg",  # Auto-detected by the model
                "source": {
                    "bytes": image_base64
                }
            }
        }
    }
    
    response = client.invoke_model(
        modelId=EMBEDDING_CONFIG["model_id"],
        body=json.dumps(request_body),
        contentType="application/json",
        accept="application/json"
    )
    
    response_body = json.loads(response['body'].read())
    return response_body['embeddings'][0]['embedding']
