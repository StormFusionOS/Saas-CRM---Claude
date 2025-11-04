"""
Copyright (c) 2025 River CityClean
SPDX-License-Identifier: MIT

Embedding Generation Service

Generates vector embeddings for text content using OpenAI or HuggingFace models.
Used for semantic search and RAG context retrieval.
"""

from typing import List, Dict, Any, Optional
import structlog
from enum import Enum

logger = structlog.get_logger(__name__)


class EmbeddingProvider(str, Enum):
    """Supported embedding providers."""
    OPENAI = "openai"
    HUGGINGFACE = "huggingface"
    MOCK = "mock"  # For testing without API keys


class EmbeddingService:
    """
    Service for generating text embeddings.

    Supports multiple providers with fallback to mock for development.
    """

    def __init__(
        self,
        provider: EmbeddingProvider = EmbeddingProvider.MOCK,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize embedding service.

        Args:
            provider: Embedding provider to use
            model_name: Specific model (e.g., 'text-embedding-ada-002')
            api_key: API key for provider
        """
        self.provider = provider
        self.model_name = model_name or self._default_model()
        self.api_key = api_key
        self.logger = logger.bind(service="embedding", provider=provider)

        # Initialize client based on provider
        self.client = None
        if provider == EmbeddingProvider.OPENAI:
            self._init_openai()
        elif provider == EmbeddingProvider.HUGGINGFACE:
            self._init_huggingface()

    def _default_model(self) -> str:
        """Get default model for provider."""
        defaults = {
            EmbeddingProvider.OPENAI: "text-embedding-ada-002",
            EmbeddingProvider.HUGGINGFACE: "sentence-transformers/all-MiniLM-L6-v2",
            EmbeddingProvider.MOCK: "mock-embeddings-1536"
        }
        return defaults.get(self.provider, "text-embedding-ada-002")

    def _init_openai(self):
        """Initialize OpenAI client."""
        try:
            import openai
            if self.api_key:
                openai.api_key = self.api_key
            self.client = openai
            self.logger.info("openai_initialized", model=self.model_name)
        except ImportError:
            self.logger.warning("openai_not_installed", fallback="mock")
            self.provider = EmbeddingProvider.MOCK

    def _init_huggingface(self):
        """Initialize HuggingFace client."""
        try:
            from sentence_transformers import SentenceTransformer
            self.client = SentenceTransformer(self.model_name)
            self.logger.info("huggingface_initialized", model=self.model_name)
        except ImportError:
            self.logger.warning("sentence_transformers_not_installed", fallback="mock")
            self.provider = EmbeddingProvider.MOCK

    # ==========================================================================
    # Embedding Generation
    # ==========================================================================

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            List of floats (embedding vector)
        """
        if not text or not text.strip():
            return self._zero_embedding()

        try:
            if self.provider == EmbeddingProvider.OPENAI:
                return self._embed_openai(text)
            elif self.provider == EmbeddingProvider.HUGGINGFACE:
                return self._embed_huggingface(text)
            else:
                return self._embed_mock(text)

        except Exception as e:
            self.logger.error("embedding_failed", text_length=len(text), error=str(e))
            return self._zero_embedding()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch processing).

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        try:
            if self.provider == EmbeddingProvider.OPENAI:
                return self._embed_batch_openai(texts)
            elif self.provider == EmbeddingProvider.HUGGINGFACE:
                return self._embed_batch_huggingface(texts)
            else:
                return [self._embed_mock(t) for t in texts]

        except Exception as e:
            self.logger.error("batch_embedding_failed", count=len(texts), error=str(e))
            return [self._zero_embedding() for _ in texts]

    # ==========================================================================
    # Provider-Specific Methods
    # ==========================================================================

    def _embed_openai(self, text: str) -> List[float]:
        """Generate embedding using OpenAI."""
        response = self.client.Embedding.create(
            input=text,
            model=self.model_name
        )
        return response['data'][0]['embedding']

    def _embed_batch_openai(self, texts: List[str]) -> List[List[float]]:
        """Batch embed using OpenAI."""
        response = self.client.Embedding.create(
            input=texts,
            model=self.model_name
        )
        return [item['embedding'] for item in response['data']]

    def _embed_huggingface(self, text: str) -> List[float]:
        """Generate embedding using HuggingFace."""
        embedding = self.client.encode(text)
        return embedding.tolist()

    def _embed_batch_huggingface(self, texts: List[str]) -> List[List[float]]:
        """Batch embed using HuggingFace."""
        embeddings = self.client.encode(texts)
        return embeddings.tolist()

    def _embed_mock(self, text: str) -> List[float]:
        """
        Generate mock embedding for testing.

        Uses deterministic hash-based generation so same text = same embedding.
        """
        import hashlib
        import numpy as np

        # Hash text to seed
        seed = int(hashlib.sha256(text.encode()).hexdigest()[:8], 16)
        np.random.seed(seed)

        # Generate 1536-dimensional vector (OpenAI ada-002 size)
        embedding = np.random.randn(1536).astype(np.float32)

        # Normalize to unit length
        embedding = embedding / np.linalg.norm(embedding)

        return embedding.tolist()

    def _zero_embedding(self) -> List[float]:
        """Return zero vector for errors."""
        return [0.0] * 1536

    # ==========================================================================
    # Utility Methods
    # ==========================================================================

    def get_embedding_dimension(self) -> int:
        """Get dimensionality of embeddings."""
        dimensions = {
            "text-embedding-ada-002": 1536,
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "sentence-transformers/all-MiniLM-L6-v2": 384,
            "mock-embeddings-1536": 1536
        }
        return dimensions.get(self.model_name, 1536)

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Uses rough approximation: 1 token ≈ 4 characters.
        """
        return len(text) // 4

    def truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """
        Truncate text to approximate token limit.

        Args:
            text: Text to truncate
            max_tokens: Maximum tokens

        Returns:
            Truncated text
        """
        max_chars = max_tokens * 4
        if len(text) <= max_chars:
            return text

        return text[:max_chars] + "..."


# ==============================================================================
# Global Instance (Singleton Pattern)
# ==============================================================================

_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service(
    provider: EmbeddingProvider = EmbeddingProvider.MOCK,
    model_name: Optional[str] = None,
    api_key: Optional[str] = None
) -> EmbeddingService:
    """
    Get or create embedding service instance.

    Args:
        provider: Embedding provider
        model_name: Model to use
        api_key: API key

    Returns:
        EmbeddingService instance
    """
    global _embedding_service

    if _embedding_service is None:
        _embedding_service = EmbeddingService(
            provider=provider,
            model_name=model_name,
            api_key=api_key
        )

    return _embedding_service
