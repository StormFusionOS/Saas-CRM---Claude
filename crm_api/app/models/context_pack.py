"""
Copyright (c) 2025 River CityClean
SPDX-License-Identifier: MIT

Context Pack Data Models

Defines structured context packages for RAG (Retrieval Augmented Generation).
Context packs bundle relevant information with provenance and token budgets.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class SourceType(str, Enum):
    """Types of content sources."""
    OUR_PAGE = "our_page"
    COMPETITOR = "competitor"
    SERP_SNIPPET = "serp_snippet"
    PAA_QUESTION = "paa_question"
    INTERNAL_LINK = "internal_link"
    BACKLINK = "backlink"
    SCHEMA_MARKUP = "schema_markup"
    KEYWORD_DATA = "keyword_data"


class ContextSource(BaseModel):
    """Single source of context with provenance."""
    source_type: SourceType
    source_id: str  # e.g., "page:123", "competitor:456", "serp:789"
    url: Optional[str] = None
    title: Optional[str] = None
    snippet: str
    snippet_tokens: int
    relevance_score: float = Field(ge=0.0, le=1.0)
    metadata: Dict[str, Any] = {}


class TokenBudget(BaseModel):
    """Token allocation strategy for context pack."""
    total_budget: int = 1500  # Max tokens for entire context
    our_page_tokens: int = 500
    competitor_tokens: int = 400
    serp_tokens: int = 300
    keyword_data_tokens: int = 200
    buffer_tokens: int = 100  # Reserved for prompts


class ContextPack(BaseModel):
    """
    Assembled context package for RAG prompts.

    Contains all relevant context with provenance and token tracking.
    """
    pack_id: str
    created_at: datetime = Field(default_factory=datetime.now)

    # Target
    target_page_id: Optional[int] = None
    target_url: Optional[str] = None
    target_keyword: Optional[str] = None

    # Context Sources
    our_page: Optional[ContextSource] = None
    competitors: List[ContextSource] = []
    serp_snippets: List[ContextSource] = []
    paa_questions: List[ContextSource] = []
    related_keywords: List[Dict[str, Any]] = []

    # Token Management
    budget: TokenBudget = Field(default_factory=TokenBudget)
    actual_tokens: int = 0
    is_truncated: bool = False

    # Metadata
    retrieval_strategy: str = "hybrid"  # semantic, keyword, hybrid
    retrieved_from_collections: List[str] = []
    query_embedding_model: Optional[str] = None


class RetrievalQuery(BaseModel):
    """Query parameters for context retrieval."""
    # Target
    page_id: Optional[int] = None
    page_url: Optional[str] = None
    keyword: Optional[str] = None

    # Query Text
    query_text: str
    query_embedding: Optional[List[float]] = None

    # Filters
    domain_filter: Optional[str] = None
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None

    # Limits
    max_competitors: int = 5
    max_serp_results: int = 10
    max_paa: int = 5

    # Thresholds
    min_relevance_score: float = 0.7


class RAGChainStep(str, Enum):
    """Steps in the RAG chain pipeline."""
    RETRIEVAL = "retrieval"
    TEMPLATING = "templating"
    GENERATION = "generation"
    VALIDATION = "validation"
    STORAGE = "storage"


class RAGChainResult(BaseModel):
    """Result from RAG chain execution."""
    chain_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None

    # Steps
    current_step: RAGChainStep = RAGChainStep.RETRIEVAL
    steps_completed: List[RAGChainStep] = []
    steps_failed: List[RAGChainStep] = []

    # Context
    context_pack: Optional[ContextPack] = None

    # Generated Content
    prompt_template: Optional[str] = None
    final_prompt: Optional[str] = None
    generated_text: Optional[str] = None
    confidence_score: Optional[float] = None

    # Validation
    validation_passed: bool = False
    validation_errors: List[str] = []

    # Storage
    change_log_id: Optional[int] = None
    task_log_id: Optional[int] = None

    # Metadata
    model_used: Optional[str] = None
    total_tokens_used: Optional[int] = None
    error_message: Optional[str] = None


class CompetitorSnapshot(BaseModel):
    """Competitor page analysis snapshot."""
    competitor_id: str
    url: str
    domain: str
    title: Optional[str] = None
    meta_description: Optional[str] = None
    content_preview: str
    word_count: int
    rank_position: Optional[int] = None
    has_featured_snippet: bool = False
    schema_types: List[str] = []
    backlink_count: Optional[int] = None
    domain_authority: Optional[float] = None


class SERPContext(BaseModel):
    """SERP data context for a keyword."""
    keyword: str
    search_volume: Optional[int] = None
    current_rank: Optional[int] = None

    # Top Results
    top_results: List[Dict[str, Any]] = []
    featured_snippet: Optional[Dict[str, Any]] = None
    paa_questions: List[str] = []
    related_searches: List[str] = []

    # Our Performance
    our_url: Optional[str] = None
    our_rank: Optional[int] = None
    our_impressions: Optional[int] = None
    our_clicks: Optional[int] = None
    our_ctr: Optional[float] = None


# ==============================================================================
# Helper Functions
# ==============================================================================

def estimate_tokens(text: str) -> int:
    """
    Estimate token count for text.

    Uses rough approximation: 1 token ≈ 4 characters.
    """
    return len(text) // 4


def truncate_to_budget(text: str, max_tokens: int) -> tuple[str, bool]:
    """
    Truncate text to fit token budget.

    Args:
        text: Text to truncate
        max_tokens: Maximum tokens allowed

    Returns:
        Tuple of (truncated_text, was_truncated)
    """
    current_tokens = estimate_tokens(text)

    if current_tokens <= max_tokens:
        return text, False

    # Truncate to 90% of budget to be safe
    target_chars = int(max_tokens * 4 * 0.9)
    truncated = text[:target_chars] + "..."

    return truncated, True


def create_context_source(
    source_type: SourceType,
    source_id: str,
    snippet: str,
    url: Optional[str] = None,
    title: Optional[str] = None,
    relevance_score: float = 1.0,
    max_tokens: Optional[int] = None
) -> ContextSource:
    """
    Factory function to create ContextSource with automatic token counting.

    Args:
        source_type: Type of source
        source_id: Unique identifier
        snippet: Text content
        url: Source URL
        title: Source title
        relevance_score: Relevance score (0.0-1.0)
        max_tokens: Optional token limit (will truncate)

    Returns:
        ContextSource instance
    """
    # Truncate if needed
    final_snippet = snippet
    if max_tokens:
        final_snippet, _ = truncate_to_budget(snippet, max_tokens)

    return ContextSource(
        source_type=source_type,
        source_id=source_id,
        url=url,
        title=title,
        snippet=final_snippet,
        snippet_tokens=estimate_tokens(final_snippet),
        relevance_score=relevance_score
    )
