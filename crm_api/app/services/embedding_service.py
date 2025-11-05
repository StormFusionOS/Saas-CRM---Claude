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
from .qdrant_service import QdrantService, COLLECTION_SCRAPE_PAGES, COLLECTION_SERP_SNIPPETS

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
        api_key: Optional[str] = None,
        qdrant_service: Optional[QdrantService] = None
    ):
        """
        Initialize embedding service.

        Args:
            provider: Embedding provider to use
            model_name: Specific model (e.g., 'text-embedding-ada-002')
            api_key: API key for provider
            qdrant_service: Qdrant service instance for storing embeddings
        """
        self.provider = provider
        self.model_name = model_name or self._default_model()
        self.api_key = api_key
        self.qdrant_service = qdrant_service
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

    # ==========================================================================
    # Scrape Suite Methods
    # ==========================================================================

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Alias for embed_batch for Scrape Suite compatibility.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        return self.embed_batch(texts)

    def upsert_page_embedding(
        self,
        page_id: int,
        site_id: int,
        url: str,
        title: str,
        page_type: str,
        chunks: List[str]
    ) -> bool:
        """
        Embed and upsert competitor page content to Qdrant.

        Args:
            page_id: Database ID of the page
            site_id: ID of the competitor site
            url: Page URL
            title: Page title
            page_type: Type of page (homepage, blog, product, etc.)
            chunks: List of text chunks from the page

        Returns:
            True on success
        """
        if not self.qdrant_service:
            self.logger.warning("qdrant_service_not_configured")
            return False

        if not chunks:
            self.logger.warning("no_chunks_to_embed", page_id=page_id)
            return False

        try:
            # Generate embeddings for all chunks
            embeddings = self.embed_texts(chunks)

            # Upsert each chunk with metadata
            points = []
            for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                point_id = f"page_{page_id}_chunk_{idx}"
                payload = {
                    "page_id": page_id,
                    "site_id": site_id,
                    "url": url,
                    "title": title,
                    "page_type": page_type,
                    "chunk_index": idx,
                    "chunk_text": chunk,
                    "text": chunk  # For RAG compatibility
                }

                points.append({
                    "id": point_id,
                    "embedding": embedding,
                    "payload": payload
                })

            self.qdrant_service.upsert_embeddings_batch(
                collection_name=COLLECTION_SCRAPE_PAGES,
                points=points
            )

            self.logger.info(
                "page_embeddings_upserted",
                page_id=page_id,
                chunks=len(chunks)
            )
            return True

        except Exception as e:
            self.logger.error(
                "page_embedding_upsert_failed",
                page_id=page_id,
                error=str(e)
            )
            return False

    def upsert_serp_embedding(
        self,
        result_id: int,
        snapshot_id: int,
        url: str,
        snippet: str,
        query: str
    ) -> bool:
        """
        Embed and upsert SERP snippet to Qdrant.

        Args:
            result_id: Database ID of the SERP result
            snapshot_id: ID of the SERP snapshot
            url: Result URL
            snippet: SERP snippet text
            query: Search query that produced this result

        Returns:
            True on success
        """
        if not self.qdrant_service:
            self.logger.warning("qdrant_service_not_configured")
            return False

        if not snippet or not snippet.strip():
            self.logger.warning("empty_snippet", result_id=result_id)
            return False

        try:
            # Combine query context with snippet for better semantic search
            text_to_embed = f"Query: {query}\n\nSnippet: {snippet}"
            embedding = self.embed_text(text_to_embed)

            # Upsert to Qdrant
            payload = {
                "result_id": result_id,
                "snapshot_id": snapshot_id,
                "url": url,
                "snippet": snippet,
                "query": query,
                "text": snippet  # For RAG compatibility
            }

            self.qdrant_service.upsert_embedding(
                collection_name=COLLECTION_SERP_SNIPPETS,
                point_id=f"serp_{result_id}",
                embedding=embedding,
                payload=payload
            )

            self.logger.info(
                "serp_embedding_upserted",
                result_id=result_id,
                query=query
            )
            return True

        except Exception as e:
            self.logger.error(
                "serp_embedding_upsert_failed",
                result_id=result_id,
                error=str(e)
            )
            return False


# ==============================================================================
# Global Instance (Singleton Pattern)
# ==============================================================================

_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service(
    provider: EmbeddingProvider = EmbeddingProvider.MOCK,
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    qdrant_service: Optional[QdrantService] = None
) -> EmbeddingService:
    """
    Get or create embedding service instance.

    Args:
        provider: Embedding provider
        model_name: Model to use
        api_key: API key
        qdrant_service: Qdrant service instance

    Returns:
        EmbeddingService instance
    """
    global _embedding_service

    if _embedding_service is None:
        _embedding_service = EmbeddingService(
            provider=provider,
            model_name=model_name,
            api_key=api_key,
            qdrant_service=qdrant_service
        )

    return _embedding_service
