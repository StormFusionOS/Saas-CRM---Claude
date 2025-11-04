"""
Copyright (c) 2025 River CityClean
SPDX-License-Identifier: MIT

Qdrant Vector Database Service

Provides embedding storage and semantic search capabilities for:
- Page content similarity
- Keyword clustering
- RAG (Retrieval Augmented Generation)
- Prompt library search
"""

from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from qdrant_client.http import models
import numpy as np
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)


class QdrantService:
    """
    Service for interacting with Qdrant vector database.

    Provides methods for storing and searching embeddings.
    """

    def __init__(self, host: str = "localhost", port: int = 6333):
        """
        Initialize Qdrant client.

        Args:
            host: Qdrant server host
            port: Qdrant server port
        """
        self.client = QdrantClient(host=host, port=port)
        self.logger = logger.bind(service="qdrant")

    # ==============================================================================
    # Collection Management
    # ==============================================================================

    def create_collection_if_not_exists(
        self,
        collection_name: str,
        vector_size: int = 1536,  # OpenAI text-embedding-ada-002 size
        distance: Distance = Distance.COSINE
    ) -> bool:
        """
        Create a collection if it doesn't exist.

        Args:
            collection_name: Name of the collection
            vector_size: Dimension of embeddings
            distance: Distance metric (COSINE, EUCLID, DOT)

        Returns:
            True if created, False if already exists
        """
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == collection_name for c in collections)

            if not exists:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=distance
                    )
                )
                self.logger.info(
                    "collection_created",
                    collection=collection_name,
                    vector_size=vector_size
                )
                return True
            return False

        except Exception as e:
            self.logger.error(
                "collection_creation_failed",
                collection=collection_name,
                error=str(e)
            )
            raise

    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection."""
        try:
            self.client.delete_collection(collection_name=collection_name)
            self.logger.info("collection_deleted", collection=collection_name)
            return True
        except Exception as e:
            self.logger.error(
                "collection_deletion_failed",
                collection=collection_name,
                error=str(e)
            )
            return False

    # ==============================================================================
    # Embedding Storage
    # ==============================================================================

    def upsert_embedding(
        self,
        collection_name: str,
        point_id: str,
        embedding: List[float],
        payload: Dict[str, Any]
    ) -> bool:
        """
        Insert or update an embedding.

        Args:
            collection_name: Collection to store in
            point_id: Unique ID for this point
            embedding: Vector embedding
            payload: Metadata to store with embedding

        Returns:
            True on success
        """
        try:
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload=payload
            )

            self.client.upsert(
                collection_name=collection_name,
                points=[point]
            )

            self.logger.debug(
                "embedding_upserted",
                collection=collection_name,
                point_id=point_id
            )
            return True

        except Exception as e:
            self.logger.error(
                "embedding_upsert_failed",
                collection=collection_name,
                point_id=point_id,
                error=str(e)
            )
            raise

    def upsert_embeddings_batch(
        self,
        collection_name: str,
        points: List[Dict[str, Any]]
    ) -> bool:
        """
        Batch insert/update embeddings.

        Args:
            collection_name: Collection to store in
            points: List of dicts with 'id', 'embedding', 'payload'

        Returns:
            True on success
        """
        try:
            qdrant_points = [
                PointStruct(
                    id=p["id"],
                    vector=p["embedding"],
                    payload=p.get("payload", {})
                )
                for p in points
            ]

            self.client.upsert(
                collection_name=collection_name,
                points=qdrant_points
            )

            self.logger.info(
                "batch_embeddings_upserted",
                collection=collection_name,
                count=len(points)
            )
            return True

        except Exception as e:
            self.logger.error(
                "batch_upsert_failed",
                collection=collection_name,
                error=str(e)
            )
            raise

    # ==============================================================================
    # Semantic Search
    # ==============================================================================

    def search_similar(
        self,
        collection_name: str,
        query_embedding: List[float],
        limit: int = 10,
        score_threshold: Optional[float] = None,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings.

        Args:
            collection_name: Collection to search
            query_embedding: Query vector
            limit: Number of results
            score_threshold: Minimum similarity score
            filter_conditions: Metadata filters

        Returns:
            List of matches with id, score, and payload
        """
        try:
            # Build filter if provided
            query_filter = None
            if filter_conditions:
                query_filter = Filter(
                    must=[
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                        for key, value in filter_conditions.items()
                    ]
                )

            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=query_filter
            )

            matches = [
                {
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload
                }
                for hit in results
            ]

            self.logger.debug(
                "search_completed",
                collection=collection_name,
                results=len(matches)
            )

            return matches

        except Exception as e:
            self.logger.error(
                "search_failed",
                collection=collection_name,
                error=str(e)
            )
            raise

    def search_by_id(
        self,
        collection_name: str,
        point_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find similar items to a specific point ID.

        Args:
            collection_name: Collection to search
            point_id: ID of the reference point
            limit: Number of results

        Returns:
            List of similar items
        """
        try:
            # Get the point
            point = self.client.retrieve(
                collection_name=collection_name,
                ids=[point_id]
            )

            if not point:
                return []

            # Search for similar
            return self.search_similar(
                collection_name=collection_name,
                query_embedding=point[0].vector,
                limit=limit + 1  # +1 to exclude self
            )[1:]  # Skip first result (self)

        except Exception as e:
            self.logger.error(
                "search_by_id_failed",
                collection=collection_name,
                point_id=point_id,
                error=str(e)
            )
            raise

    # ==============================================================================
    # Retrieval (for RAG)
    # ==============================================================================

    def retrieve_context(
        self,
        collection_name: str,
        query_embedding: List[float],
        limit: int = 5,
        min_score: float = 0.7
    ) -> List[str]:
        """
        Retrieve relevant context for RAG (Retrieval Augmented Generation).

        Args:
            collection_name: Collection to search
            query_embedding: Query embedding
            limit: Max results
            min_score: Minimum similarity score

        Returns:
            List of text chunks for context
        """
        results = self.search_similar(
            collection_name=collection_name,
            query_embedding=query_embedding,
            limit=limit,
            score_threshold=min_score
        )

        contexts = [
            hit["payload"].get("text", "")
            for hit in results
            if "text" in hit["payload"]
        ]

        return contexts

    # ==============================================================================
    # Deletion
    # ==============================================================================

    def delete_point(self, collection_name: str, point_id: str) -> bool:
        """Delete a single point."""
        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=models.PointIdsList(
                    points=[point_id]
                )
            )
            return True
        except Exception as e:
            self.logger.error(
                "point_deletion_failed",
                collection=collection_name,
                point_id=point_id,
                error=str(e)
            )
            return False

    def delete_points_by_filter(
        self,
        collection_name: str,
        filter_conditions: Dict[str, Any]
    ) -> bool:
        """Delete points matching filter."""
        try:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                    for key, value in filter_conditions.items()
                ]
            )

            self.client.delete(
                collection_name=collection_name,
                points_selector=models.FilterSelector(
                    filter=query_filter
                )
            )
            return True
        except Exception as e:
            self.logger.error(
                "filtered_deletion_failed",
                collection=collection_name,
                error=str(e)
            )
            return False

    # ==============================================================================
    # Health & Stats
    # ==============================================================================

    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get collection statistics."""
        try:
            info = self.client.get_collection(collection_name=collection_name)
            return {
                "name": collection_name,
                "points_count": info.points_count,
                "segments_count": info.segments_count,
                "status": info.status,
                "vector_size": info.config.params.vectors.size,
                "distance": info.config.params.vectors.distance
            }
        except Exception as e:
            self.logger.error(
                "collection_info_failed",
                collection=collection_name,
                error=str(e)
            )
            return {}

    def health_check(self) -> bool:
        """Check if Qdrant is healthy."""
        try:
            collections = self.client.get_collections()
            return True
        except Exception:
            return False


# ==============================================================================
# Collection Constants
# ==============================================================================

COLLECTION_PAGE_CONTENT = "page_content"
COLLECTION_SERP_RESULTS = "serp_results"
COLLECTION_PROMPT_LIBRARY = "prompt_library"
COLLECTION_KEYWORD_CLUSTERS = "keyword_clusters"


# ==============================================================================
# Helper: Initialize Default Collections
# ==============================================================================

def initialize_collections(qdrant_host: str = "localhost", qdrant_port: int = 6333):
    """
    Initialize all required Qdrant collections.

    Call this on application startup.
    """
    service = QdrantService(host=qdrant_host, port=qdrant_port)

    collections = [
        {
            "name": COLLECTION_PAGE_CONTENT,
            "vector_size": 1536,  # OpenAI ada-002
            "distance": Distance.COSINE
        },
        {
            "name": COLLECTION_SERP_RESULTS,
            "vector_size": 1536,
            "distance": Distance.COSINE
        },
        {
            "name": COLLECTION_PROMPT_LIBRARY,
            "vector_size": 1536,
            "distance": Distance.COSINE
        },
        {
            "name": COLLECTION_KEYWORD_CLUSTERS,
            "vector_size": 1536,
            "distance": Distance.COSINE
        }
    ]

    for collection in collections:
        service.create_collection_if_not_exists(
            collection_name=collection["name"],
            vector_size=collection["vector_size"],
            distance=collection["distance"]
        )

    logger.info("qdrant_collections_initialized", count=len(collections))
