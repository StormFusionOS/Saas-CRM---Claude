"""
Copyright (c) 2025 River CityClean
SPDX-License-Identifier: MIT

RAG API Endpoints

Provides endpoints for context retrieval and AI generation pipeline.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.services.rag_service import get_rag_service, RAGService
from app.models.context_pack import (
    ContextPack,
    RetrievalQuery,
    TokenBudget,
    RAGChainResult,
    SERPContext
)
from app.api.deps import require_sales_claims

router = APIRouter(prefix="/rag", tags=["RAG"])


# ==============================================================================
# Request/Response Models
# ==============================================================================

class RetrieveContextRequest(BaseModel):
    """Request for context retrieval."""
    query_text: str = Field(..., description="Query text for semantic search")
    page_id: Optional[int] = None
    page_url: Optional[str] = None
    keyword: Optional[str] = None
    max_competitors: int = 5
    max_serp_results: int = 10
    max_paa: int = 5
    min_relevance_score: float = 0.7
    token_budget: Optional[TokenBudget] = None


class ExecuteRAGChainRequest(BaseModel):
    """Request for full RAG chain execution."""
    query_text: str
    page_id: Optional[int] = None
    page_url: Optional[str] = None
    keyword: Optional[str] = None
    prompt_template: str = Field(
        ...,
        description="Prompt template with {context}, {keyword}, {url} placeholders"
    )
    module_name: str = Field(..., description="AI module name (e.g., 'ctr_optimizer')")
    action: str = Field(..., description="Action type (e.g., 'update_meta_title')")
    target: str = Field(..., description="Target resource (e.g., 'page:123')")


class EmbedTextRequest(BaseModel):
    """Request for embedding generation."""
    text: str = Field(..., description="Text to embed")


class EmbedBatchRequest(BaseModel):
    """Request for batch embedding generation."""
    texts: List[str] = Field(..., description="List of texts to embed")


class EmbedTextResponse(BaseModel):
    """Response for embedding generation."""
    embedding: List[float]
    dimension: int
    model: str


class EmbedBatchResponse(BaseModel):
    """Response for batch embedding generation."""
    embeddings: List[List[float]]
    count: int
    dimension: int
    model: str


# ==============================================================================
# Context Retrieval Endpoints
# ==============================================================================

@router.post("/retrieve-context", response_model=ContextPack)
def retrieve_context(
    request: RetrieveContextRequest,
    current_user: dict = Depends(require_sales_claims)
) -> ContextPack:
    """
    Retrieve and assemble context pack for RAG.

    Performs semantic search across Qdrant collections and assembles
    context from our pages, competitors, SERP, and PAA.

    **Token Budget:**
    - Total: 1500 tokens
    - Our page: 500 tokens
    - Competitors: 400 tokens
    - SERP: 300 tokens
    - Keywords: 200 tokens
    - Buffer: 100 tokens
    """
    try:
        rag_service = get_rag_service()

        query = RetrievalQuery(
            query_text=request.query_text,
            page_id=request.page_id,
            page_url=request.page_url,
            keyword=request.keyword,
            max_competitors=request.max_competitors,
            max_serp_results=request.max_serp_results,
            max_paa=request.max_paa,
            min_relevance_score=request.min_relevance_score
        )

        context_pack = rag_service.retrieve_context(
            query=query,
            budget=request.token_budget
        )

        return context_pack

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Context retrieval failed: {str(e)}")


@router.post("/assemble-prompt", response_model=dict)
def assemble_prompt(
    context_pack: ContextPack,
    current_user: dict = Depends(require_sales_claims)
) -> Dict[str, Any]:
    """
    Assemble context pack into formatted prompt context.

    Takes a ContextPack and formats it into a readable context string
    suitable for LLM prompts.
    """
    try:
        rag_service = get_rag_service()
        context_text = rag_service.assemble_prompt_context(context_pack)

        return {
            "context_text": context_text,
            "token_estimate": len(context_text) // 4,
            "pack_id": context_pack.pack_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prompt assembly failed: {str(e)}")


# ==============================================================================
# RAG Chain Execution
# ==============================================================================

@router.post("/execute-chain", response_model=RAGChainResult)
def execute_rag_chain(
    request: ExecuteRAGChainRequest,
    current_user: dict = Depends(require_sales_claims)
) -> RAGChainResult:
    """
    Execute full RAG chain pipeline.

    **Pipeline Steps:**
    1. **Retrieval** - Fetch context from Qdrant and database
    2. **Templating** - Insert context into prompt template
    3. **Generation** - Generate content with LLM (currently mock)
    4. **Validation** - Validate generated content
    5. **Storage** - Save to change_log as pending suggestion

    **Example Prompt Template:**
    ```
    You are an SEO expert. Based on the following context:

    {context}

    Generate an optimized meta title for the page: {url}
    Target keyword: {keyword}
    ```
    """
    try:
        rag_service = get_rag_service()

        query = RetrievalQuery(
            query_text=request.query_text,
            page_id=request.page_id,
            page_url=request.page_url,
            keyword=request.keyword
        )

        result = rag_service.execute_rag_chain(
            query=query,
            prompt_template=request.prompt_template,
            module_name=request.module_name,
            action=request.action,
            target=request.target
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG chain execution failed: {str(e)}")


# ==============================================================================
# Embedding Generation Endpoints
# ==============================================================================

@router.post("/embed", response_model=EmbedTextResponse)
def embed_text(
    request: EmbedTextRequest,
    current_user: dict = Depends(require_sales_claims)
) -> EmbedTextResponse:
    """
    Generate embedding for a single text.

    Uses the configured embedding provider (OpenAI, HuggingFace, or mock).
    Embeddings are 1536-dimensional vectors.
    """
    try:
        rag_service = get_rag_service()
        embedding = rag_service.embeddings.embed_text(request.text)

        return EmbedTextResponse(
            embedding=embedding,
            dimension=len(embedding),
            model=rag_service.embeddings.model_name
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {str(e)}")


@router.post("/embed-batch", response_model=EmbedBatchResponse)
def embed_batch(
    request: EmbedBatchRequest,
    current_user: dict = Depends(require_sales_claims)
) -> EmbedBatchResponse:
    """
    Generate embeddings for multiple texts (batch processing).

    More efficient than multiple single embed calls.
    """
    try:
        rag_service = get_rag_service()
        embeddings = rag_service.embeddings.embed_batch(request.texts)

        return EmbedBatchResponse(
            embeddings=embeddings,
            count=len(embeddings),
            dimension=len(embeddings[0]) if embeddings else 0,
            model=rag_service.embeddings.model_name
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch embedding failed: {str(e)}")


# ==============================================================================
# Utility Endpoints
# ==============================================================================

@router.get("/health")
def health_check(current_user: dict = Depends(require_sales_claims)) -> Dict[str, Any]:
    """
    Check RAG service health.

    Verifies:
    - Qdrant connection
    - Embedding service
    - Available collections
    """
    try:
        rag_service = get_rag_service()

        qdrant_healthy = rag_service.qdrant.health_check()
        collections = rag_service.qdrant.client.get_collections().collections

        return {
            "status": "healthy" if qdrant_healthy else "degraded",
            "qdrant_connected": qdrant_healthy,
            "embedding_provider": rag_service.embeddings.provider.value,
            "embedding_model": rag_service.embeddings.model_name,
            "collections_available": [c.name for c in collections],
            "collections_count": len(collections)
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.get("/collections/{collection_name}/info")
def get_collection_info(
    collection_name: str,
    current_user: dict = Depends(require_sales_claims)
) -> Dict[str, Any]:
    """Get information about a specific Qdrant collection."""
    try:
        rag_service = get_rag_service()
        info = rag_service.qdrant.get_collection_info(collection_name)

        if not info:
            raise HTTPException(status_code=404, detail=f"Collection '{collection_name}' not found")

        return info

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get collection info: {str(e)}")


@router.post("/collections/{collection_name}/search")
def search_collection(
    collection_name: str,
    query_text: str,
    limit: int = 10,
    min_score: float = 0.7,
    current_user: dict = Depends(require_sales_claims)
) -> List[Dict[str, Any]]:
    """
    Search a Qdrant collection semantically.

    Embeds the query text and finds similar items.
    """
    try:
        rag_service = get_rag_service()

        # Generate embedding for query
        query_embedding = rag_service.embeddings.embed_text(query_text)

        # Search
        results = rag_service.qdrant.search_similar(
            collection_name=collection_name,
            query_embedding=query_embedding,
            limit=limit,
            score_threshold=min_score
        )

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
