"""
Embedding Service for Meridian.

Generates text embeddings via Amazon Bedrock with model fallbacks.
"""

import json
import os
from typing import List, Optional

import boto3


class EmbeddingService:
    """Bedrock embeddings — Cohere Embed v4 by default (1024d for Aurora pgvector)."""

    PRIMARY_MODEL = "cohere.embed-v4:0"
    FALLBACK_MODELS = (
        "cohere.embed-english-v3",
        "amazon.titan-embed-text-v2:0",
    )
    DEFAULT_DIMENSIONS = 1024
    MAX_TEXT_LENGTH = 2048

    def __init__(self, region: Optional[str] = None, dimensions: Optional[int] = None):
        self.region = region or os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.dimensions = dimensions or int(os.getenv("EMBEDDING_DIMENSION", self.DEFAULT_DIMENSIONS))
        self._bedrock_client = None
        configured = os.getenv("EMBEDDING_MODEL", self.PRIMARY_MODEL)
        self.model_candidates: List[str] = [configured]
        for model_id in (self.PRIMARY_MODEL, *self.FALLBACK_MODELS):
            if model_id not in self.model_candidates:
                self.model_candidates.append(model_id)

    @property
    def bedrock_client(self):
        if self._bedrock_client is None:
            self._bedrock_client = boto3.client("bedrock-runtime", region_name=self.region)
        return self._bedrock_client

    @property
    def model_id(self) -> str:
        return self.model_candidates[0]

    def _build_request(self, model_id: str, text: str, input_type: str) -> dict:
        if "titan" in model_id:
            return {"inputText": text}
        body = {
            "texts": [text],
            "input_type": input_type,
            "truncate": "END",
        }
        if "embed-v4" in model_id or "embed-v4:" in model_id:
            body["embedding_types"] = ["float"]
            body["output_dimension"] = self.dimensions
        return body

    @staticmethod
    def _parse_response(model_id: str, response_body: dict) -> List[float]:
        if "titan" in model_id:
            return response_body["embedding"]
        embeddings = response_body.get("embeddings")
        if isinstance(embeddings, dict):
            for key in ("float", "int8"):
                if key in embeddings and embeddings[key]:
                    return embeddings[key][0]
        if isinstance(embeddings, list) and embeddings:
            first = embeddings[0]
            if isinstance(first, list):
                return first
        raise ValueError(f"Unexpected embedding response shape for {model_id}")

    def _invoke_model(self, model_id: str, text: str, input_type: str) -> List[float]:
        request_body = self._build_request(model_id, text, input_type)
        response = self.bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body),
            contentType="application/json",
            accept="application/json",
        )
        response_body = json.loads(response["body"].read())
        return self._parse_response(model_id, response_body)

    def generate_text_embedding(self, text: str, input_type: str = "search_document") -> List[float]:
        if len(text) > self.MAX_TEXT_LENGTH:
            text = text[: self.MAX_TEXT_LENGTH]

        last_error: Optional[Exception] = None
        for model_id in self.model_candidates:
            try:
                embedding = self._invoke_model(model_id, text, input_type)
                if len(embedding) != self.dimensions:
                    last_error = ValueError(
                        f"{model_id} returned {len(embedding)} dimensions, expected {self.dimensions}"
                    )
                    continue
                return embedding
            except Exception as exc:
                last_error = exc
                continue

        if last_error is not None:
            raise last_error
        raise RuntimeError("No embedding models configured")


_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    global _service
    if _service is None:
        _service = EmbeddingService()
    return _service
