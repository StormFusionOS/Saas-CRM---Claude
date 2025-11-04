"""
Copyright (c) 2025 River CityClean
SPDX-License-Identifier: MIT

RAG (Retrieval Augmented Generation) Service

Orchestrates context retrieval, assembly, and AI generation pipeline.
Integrates Qdrant vector search with PostgreSQL structured data.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import structlog
import uuid

from app.services.qdrant_service import QdrantService
from app.services.embedding_service import EmbeddingService, get_embedding_service
from app.models.context_pack import (
    ContextPack,
    ContextSource,
    TokenBudget,
    RetrievalQuery,
    RAGChainResult,
    RAGChainStep,
    SourceType,
    SERPContext,
    create_context_source,
    estimate_tokens,
    truncate_to_budget
)

logger = structlog.get_logger(__name__)


class RAGService:
    """
    RAG service for context retrieval and AI generation.

    Combines semantic search (Qdrant) with structured data (PostgreSQL).
    """

    def __init__(
        self,
        qdrant_service: Optional[QdrantService] = None,
        embedding_service: Optional[EmbeddingService] = None
    ):
        """
        Initialize RAG service.

        Args:
            qdrant_service: Qdrant vector database service (optional, vector search disabled if None)
            embedding_service: Embedding generation service
        """
        self.qdrant = qdrant_service  # May be None - vector search will be disabled
        self.embeddings = embedding_service or get_embedding_service()
        self.logger = logger.bind(service="rag")

    # ==========================================================================
    # Context Retrieval
    # ==========================================================================

    def retrieve_context(
        self,
        query: RetrievalQuery,
        budget: Optional[TokenBudget] = None
    ) -> ContextPack:
        """
        Retrieve and assemble context pack for RAG.

        Args:
            query: Retrieval query parameters
            budget: Token budget allocation

        Returns:
            Assembled context pack
        """
        pack_id = str(uuid.uuid4())
        budget = budget or TokenBudget()

        self.logger.info(
            "context_retrieval_started",
            pack_id=pack_id,
            query_text=query.query_text
        )

        # Generate query embedding if not provided
        if not query.query_embedding:
            query.query_embedding = self.embeddings.embed_text(query.query_text)

        # Initialize context pack
        pack = ContextPack(
            pack_id=pack_id,
            target_page_id=query.page_id,
            target_url=query.page_url,
            target_keyword=query.keyword,
            budget=budget,
            query_embedding_model=self.embeddings.model_name
        )

        # Retrieve from different sources
        try:
            # 1. Our page content
            pack.our_page = self._retrieve_our_page(query, budget.our_page_tokens)

            # 2. Competitor content
            pack.competitors = self._retrieve_competitors(
                query,
                budget.competitor_tokens,
                limit=query.max_competitors
            )

            # 3. SERP snippets
            pack.serp_snippets = self._retrieve_serp_snippets(
                query,
                budget.serp_tokens,
                limit=query.max_serp_results
            )

            # 4. PAA questions
            pack.paa_questions = self._retrieve_paa(
                query,
                budget.keyword_data_tokens // 2,
                limit=query.max_paa
            )

            # 5. Related keywords
            pack.related_keywords = self._retrieve_related_keywords(query)

            # Calculate actual token usage
            pack.actual_tokens = self._calculate_total_tokens(pack)
            pack.is_truncated = pack.actual_tokens > budget.total_budget

            self.logger.info(
                "context_retrieval_completed",
                pack_id=pack_id,
                actual_tokens=pack.actual_tokens,
                budget=budget.total_budget,
                is_truncated=pack.is_truncated
            )

            return pack

        except Exception as e:
            self.logger.error(
                "context_retrieval_failed",
                pack_id=pack_id,
                error=str(e)
            )
            raise

    def _retrieve_our_page(
        self,
        query: RetrievalQuery,
        max_tokens: int
    ) -> Optional[ContextSource]:
        """Retrieve our page content."""
        if not query.page_id and not query.page_url:
            return None

        try:
            # Search in page_content collection
            results = self.qdrant.search_similar(
                collection_name="page_content",
                query_embedding=query.query_embedding,
                limit=1,
                filter_conditions={"page_id": query.page_id} if query.page_id else None
            )

            if not results:
                return None

            hit = results[0]
            return create_context_source(
                source_type=SourceType.OUR_PAGE,
                source_id=f"page:{query.page_id or query.page_url}",
                snippet=hit["payload"].get("text", ""),
                url=hit["payload"].get("url"),
                title=hit["payload"].get("title"),
                relevance_score=hit["score"],
                max_tokens=max_tokens
            )

        except Exception as e:
            self.logger.error("our_page_retrieval_failed", error=str(e))
            return None

    def _retrieve_competitors(
        self,
        query: RetrievalQuery,
        max_tokens: int,
        limit: int = 5
    ) -> List[ContextSource]:
        """Retrieve competitor content."""
        try:
            # Search in external_content_vectors collection
            results = self.qdrant.search_similar(
                collection_name="serp_results",
                query_embedding=query.query_embedding,
                limit=limit,
                score_threshold=query.min_relevance_score
            )

            competitors = []
            tokens_per_competitor = max_tokens // max(len(results), 1)

            for hit in results:
                payload = hit["payload"]

                # Skip our own domain
                if query.page_url and payload.get("url", "").startswith(query.page_url):
                    continue

                source = create_context_source(
                    source_type=SourceType.COMPETITOR,
                    source_id=f"competitor:{payload.get('competitor_id', hit['id'])}",
                    snippet=payload.get("text", ""),
                    url=payload.get("url"),
                    title=payload.get("title"),
                    relevance_score=hit["score"],
                    max_tokens=tokens_per_competitor
                )
                competitors.append(source)

            return competitors

        except Exception as e:
            self.logger.error("competitor_retrieval_failed", error=str(e))
            return []

    def _retrieve_serp_snippets(
        self,
        query: RetrievalQuery,
        max_tokens: int,
        limit: int = 10
    ) -> List[ContextSource]:
        """Retrieve SERP snippet content."""
        try:
            results = self.qdrant.search_similar(
                collection_name="serp_results",
                query_embedding=query.query_embedding,
                limit=limit,
                score_threshold=query.min_relevance_score,
                filter_conditions={"type": "serp_snippet"}
            )

            snippets = []
            tokens_per_snippet = max_tokens // max(len(results), 1)

            for hit in results:
                payload = hit["payload"]
                source = create_context_source(
                    source_type=SourceType.SERP_SNIPPET,
                    source_id=f"serp:{hit['id']}",
                    snippet=payload.get("snippet", ""),
                    url=payload.get("url"),
                    title=payload.get("title"),
                    relevance_score=hit["score"],
                    max_tokens=tokens_per_snippet
                )
                snippets.append(source)

            return snippets

        except Exception as e:
            self.logger.error("serp_retrieval_failed", error=str(e))
            return []

    def _retrieve_paa(
        self,
        query: RetrievalQuery,
        max_tokens: int,
        limit: int = 5
    ) -> List[ContextSource]:
        """Retrieve People Also Ask questions."""
        try:
            results = self.qdrant.search_similar(
                collection_name="serp_results",
                query_embedding=query.query_embedding,
                limit=limit,
                filter_conditions={"type": "paa"}
            )

            paa_list = []
            tokens_per_item = max_tokens // max(len(results), 1)

            for hit in results:
                payload = hit["payload"]
                source = create_context_source(
                    source_type=SourceType.PAA_QUESTION,
                    source_id=f"paa:{hit['id']}",
                    snippet=payload.get("question", "") + "\n" + payload.get("answer", ""),
                    relevance_score=hit["score"],
                    max_tokens=tokens_per_item
                )
                paa_list.append(source)

            return paa_list

        except Exception as e:
            self.logger.error("paa_retrieval_failed", error=str(e))
            return []

    def _retrieve_related_keywords(self, query: RetrievalQuery) -> List[Dict[str, Any]]:
        """Retrieve related keywords (mock for now, needs DB integration)."""
        # TODO: Integrate with keywords table
        return []

    def _calculate_total_tokens(self, pack: ContextPack) -> int:
        """Calculate total tokens in context pack."""
        total = 0

        if pack.our_page:
            total += pack.our_page.snippet_tokens

        for comp in pack.competitors:
            total += comp.snippet_tokens

        for serp in pack.serp_snippets:
            total += serp.snippet_tokens

        for paa in pack.paa_questions:
            total += paa.snippet_tokens

        return total

    # ==========================================================================
    # Context Assembly
    # ==========================================================================

    def assemble_prompt_context(self, pack: ContextPack) -> str:
        """
        Assemble context pack into formatted prompt context.

        Args:
            pack: Context pack

        Returns:
            Formatted context string
        """
        sections = []

        # Our Page
        if pack.our_page:
            sections.append("# Our Current Content\n")
            sections.append(f"URL: {pack.our_page.url}\n")
            sections.append(f"Title: {pack.our_page.title}\n")
            sections.append(f"{pack.our_page.snippet}\n")

        # Competitors
        if pack.competitors:
            sections.append("\n# Top Competitor Content\n")
            for i, comp in enumerate(pack.competitors, 1):
                sections.append(f"\n## Competitor {i} (Score: {comp.relevance_score:.2f})\n")
                sections.append(f"URL: {comp.url}\n")
                sections.append(f"{comp.snippet}\n")

        # SERP Snippets
        if pack.serp_snippets:
            sections.append("\n# SERP Featured Snippets\n")
            for snippet in pack.serp_snippets[:3]:  # Top 3 only
                sections.append(f"\n- {snippet.snippet}\n")

        # PAA
        if pack.paa_questions:
            sections.append("\n# People Also Ask\n")
            for paa in pack.paa_questions:
                sections.append(f"\n- {paa.snippet}\n")

        return "".join(sections)

    # ==========================================================================
    # RAG Chain Pipeline
    # ==========================================================================

    def execute_rag_chain(
        self,
        query: RetrievalQuery,
        prompt_template: str,
        module_name: str,
        action: str,
        target: str
    ) -> RAGChainResult:
        """
        Execute full RAG chain: retrieval → templating → generation → validation → storage.

        Args:
            query: Retrieval query
            prompt_template: Prompt template with {context} placeholder
            module_name: AI module name (e.g., 'ctr_optimizer')
            action: Action type (e.g., 'update_meta_title')
            target: Target identifier (e.g., 'page:123')

        Returns:
            RAG chain result
        """
        chain_id = str(uuid.uuid4())
        result = RAGChainResult(
            chain_id=chain_id,
            started_at=datetime.now()
        )

        try:
            # Step 1: Retrieval
            self.logger.info("rag_chain_step_retrieval", chain_id=chain_id)
            result.current_step = RAGChainStep.RETRIEVAL

            context_pack = self.retrieve_context(query)
            result.context_pack = context_pack
            result.steps_completed.append(RAGChainStep.RETRIEVAL)

            # Step 2: Templating
            self.logger.info("rag_chain_step_templating", chain_id=chain_id)
            result.current_step = RAGChainStep.TEMPLATING

            context_text = self.assemble_prompt_context(context_pack)
            final_prompt = prompt_template.replace("{context}", context_text)
            final_prompt = final_prompt.replace("{keyword}", query.keyword or "")
            final_prompt = final_prompt.replace("{url}", query.page_url or "")

            result.prompt_template = prompt_template
            result.final_prompt = final_prompt
            result.steps_completed.append(RAGChainStep.TEMPLATING)

            # Step 3: Generation (mock for now - needs LLM integration)
            self.logger.info("rag_chain_step_generation", chain_id=chain_id)
            result.current_step = RAGChainStep.GENERATION

            # TODO: Integrate with LLM (OpenAI, Anthropic, etc.)
            generated_text = self._mock_generation(final_prompt)
            result.generated_text = generated_text
            result.confidence_score = 0.85  # Mock confidence
            result.steps_completed.append(RAGChainStep.GENERATION)

            # Step 4: Validation
            self.logger.info("rag_chain_step_validation", chain_id=chain_id)
            result.current_step = RAGChainStep.VALIDATION

            validation_passed, validation_errors = self._validate_generation(
                generated_text,
                action
            )
            result.validation_passed = validation_passed
            result.validation_errors = validation_errors
            result.steps_completed.append(RAGChainStep.VALIDATION)

            # Step 5: Storage (save to change_log)
            if validation_passed:
                self.logger.info("rag_chain_step_storage", chain_id=chain_id)
                result.current_step = RAGChainStep.STORAGE

                # TODO: Integrate with change_log API
                change_log_id = self._store_suggestion(
                    module_name=module_name,
                    action=action,
                    target=target,
                    proposed_value=generated_text,
                    confidence_score=result.confidence_score,
                    context_pack_id=context_pack.pack_id
                )
                result.change_log_id = change_log_id
                result.steps_completed.append(RAGChainStep.STORAGE)

            # Complete
            result.completed_at = datetime.now()
            result.duration_seconds = (
                result.completed_at - result.started_at
            ).total_seconds()

            self.logger.info(
                "rag_chain_completed",
                chain_id=chain_id,
                duration=result.duration_seconds,
                validation_passed=validation_passed
            )

            return result

        except Exception as e:
            result.error_message = str(e)
            result.steps_failed.append(result.current_step)
            self.logger.error(
                "rag_chain_failed",
                chain_id=chain_id,
                step=result.current_step,
                error=str(e)
            )
            raise

    def _mock_generation(self, prompt: str) -> str:
        """Mock LLM generation (placeholder for actual LLM integration)."""
        return f"[MOCK GENERATED CONTENT BASED ON PROMPT OF {estimate_tokens(prompt)} TOKENS]"

    def _validate_generation(self, text: str, action: str) -> tuple[bool, List[str]]:
        """
        Validate generated content.

        Args:
            text: Generated text
            action: Action type

        Returns:
            Tuple of (passed, errors)
        """
        errors = []

        # Basic validation
        if not text or len(text.strip()) == 0:
            errors.append("Generated text is empty")

        # Action-specific validation
        if action == "update_meta_title":
            if len(text) > 60:
                errors.append(f"Meta title too long: {len(text)} chars (max 60)")
            if len(text) < 30:
                errors.append(f"Meta title too short: {len(text)} chars (min 30)")

        elif action == "update_meta_description":
            if len(text) > 160:
                errors.append(f"Meta description too long: {len(text)} chars (max 160)")
            if len(text) < 120:
                errors.append(f"Meta description too short: {len(text)} chars (min 120)")

        return len(errors) == 0, errors

    def _store_suggestion(
        self,
        module_name: str,
        action: str,
        target: str,
        proposed_value: str,
        confidence_score: float,
        context_pack_id: str
    ) -> int:
        """
        Store AI suggestion in change_log.

        Args:
            module_name: AI module
            action: Action type
            target: Target resource
            proposed_value: Generated content
            confidence_score: Confidence
            context_pack_id: Context pack ID

        Returns:
            change_log ID
        """
        # TODO: Integrate with change_log API
        # For now, return mock ID
        self.logger.info(
            "suggestion_stored",
            module=module_name,
            action=action,
            target=target,
            context_pack_id=context_pack_id
        )
        return 999  # Mock ID


# ==============================================================================
# Singleton Instance
# ==============================================================================

_rag_service: Optional[RAGService] = None


def get_rag_service(
    qdrant_host: str = "localhost",
    qdrant_port: int = 6333
) -> RAGService:
    """
    Get or create RAG service instance.

    Args:
        qdrant_host: Qdrant host
        qdrant_port: Qdrant port

    Returns:
        RAGService instance
    """
    global _rag_service

    if _rag_service is None:
        qdrant = QdrantService(host=qdrant_host, port=qdrant_port)
        _rag_service = RAGService(qdrant_service=qdrant)

    return _rag_service
