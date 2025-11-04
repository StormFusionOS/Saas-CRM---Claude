"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

SEO Meta Optimizer Module
Analyzes page content and generates optimized meta titles and descriptions
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

from app.services.rag_service import RAGService, RetrievalQuery
from app.services.prompt_library import PromptLibraryService, get_prompt_library
from app.models.prompt_template import PromptTemplate, OutputType
from app.api.routes.governance import create_change_log_entry
from app.schemas.governance import ChangeLogCreate

logger = structlog.get_logger()


class SEOMetaOptimizer:
    """
    AI Module: SEO Meta Tag Optimizer

    Analyzes page content and generates optimized meta titles and descriptions
    with keyword integration, length optimization, and CTR improvements.
    """

    MODULE_NAME = "seo_meta_optimizer"

    def __init__(
        self,
        rag_service: Optional[RAGService] = None,
        prompt_service: Optional[PromptLibraryService] = None
    ):
        self.rag_service = rag_service or RAGService()
        self.prompt_service = prompt_service or get_prompt_library()
        self.logger = logger.bind(module=self.MODULE_NAME)

        # Initialize meta optimization prompt template
        self._ensure_prompt_template()

    def _ensure_prompt_template(self):
        """Ensure meta optimization prompt template exists."""
        try:
            # Try to get existing template
            self.prompt_service.get_template(
                template_name="meta_optimization",
                version="1.0.0"
            )
            self.logger.info("meta_optimization_template_found")
        except:
            # Create template if not exists
            template = PromptTemplate(
                template_id=str(uuid.uuid4()),
                template_name="meta_optimization",
                version="1.0.0",
                system_message=(
                    "You are an expert SEO consultant specializing in meta tag optimization "
                    "for commercial cleaning services. Your goal is to create compelling, "
                    "keyword-rich meta titles and descriptions that improve CTR and rankings."
                ),
                user_prompt_template="""
Analyze this page and generate optimized meta tags:

PAGE CONTENT:
{page_content}

CURRENT META TAGS:
Title: {current_title}
Description: {current_description}

PRIMARY KEYWORD: {primary_keyword}
SECONDARY KEYWORDS: {secondary_keywords}

COMPETITOR META TAGS (for reference):
{competitor_examples}

REQUIREMENTS:
1. Meta Title: 50-60 characters, include primary keyword naturally
2. Meta Description: 150-160 characters, include primary + 1-2 secondary keywords
3. Generate 3 variants for each (title and description)
4. Each variant should be unique and compelling
5. Focus on commercial cleaning industry (B2B tone)

Provide your response as JSON with this structure:
{{
  "titles": ["variant1", "variant2", "variant3"],
  "descriptions": ["variant1", "variant2", "variant3"],
  "reasoning": "explanation of keyword placement and strategy",
  "confidence": 0.85
}}
""",
                output_type=OutputType.META_VARIANTS,
                output_schema={
                    "type": "object",
                    "properties": {
                        "titles": {
                            "type": "array",
                            "items": {"type": "string", "minLength": 50, "maxLength": 60},
                            "minItems": 3,
                            "maxItems": 3
                        },
                        "descriptions": {
                            "type": "array",
                            "items": {"type": "string", "minLength": 150, "maxLength": 160},
                            "minItems": 3,
                            "maxItems": 3
                        },
                        "reasoning": {"type": "string"},
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                    },
                    "required": ["titles", "descriptions", "reasoning", "confidence"]
                },
                max_retries=3,
                retry_prompt_template=(
                    "Your previous output was invalid:\n{error_message}\n\n"
                    "Please fix: {validation_errors}\n\n"
                    "Remember: Titles must be 50-60 chars, descriptions 150-160 chars."
                )
            )

            self.prompt_service.create_template(template)
            self.logger.info("meta_optimization_template_created")

    async def analyze_page(
        self,
        page_id: int,
        page_url: str,
        page_content: str,
        current_title: str,
        current_description: str,
        primary_keyword: str,
        secondary_keywords: List[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a page and generate meta tag optimization suggestions.

        Args:
            page_id: WordPress page ID
            page_url: Page URL
            page_content: Full page content/text
            current_title: Current meta title
            current_description: Current meta description
            primary_keyword: Primary target keyword
            secondary_keywords: List of secondary keywords

        Returns:
            Dictionary with optimization results and change log ID
        """
        self.logger.info(
            "analyzing_page",
            page_id=page_id,
            page_url=page_url,
            primary_keyword=primary_keyword
        )

        try:
            # Step 1: Retrieve context via RAG
            context = await self._retrieve_context(
                page_content=page_content,
                primary_keyword=primary_keyword
            )

            # Step 2: Execute prompt template
            optimization = await self._execute_optimization(
                page_content=page_content,
                current_title=current_title,
                current_description=current_description,
                primary_keyword=primary_keyword,
                secondary_keywords=secondary_keywords or [],
                context=context
            )

            # Step 3: Select best variant
            best_title = optimization["output"]["titles"][0]
            best_description = optimization["output"]["descriptions"][0]

            # Step 4: Create change log entry for governance review
            change_log = await self._create_change_log(
                page_id=page_id,
                page_url=page_url,
                current_title=current_title,
                current_description=current_description,
                new_title=best_title,
                new_description=best_description,
                reasoning=optimization["output"]["reasoning"],
                confidence=optimization["output"]["confidence"],
                all_variants=optimization["output"]
            )

            self.logger.info(
                "page_analyzed",
                page_id=page_id,
                change_id=change_log.change_id,
                confidence=optimization["output"]["confidence"]
            )

            return {
                "success": True,
                "page_id": page_id,
                "change_id": change_log.change_id,
                "optimization": optimization["output"],
                "execution_time_ms": optimization.get("execution_time_ms", 0)
            }

        except Exception as e:
            self.logger.error(
                "page_analysis_failed",
                page_id=page_id,
                error=str(e),
                exc_info=True
            )
            return {
                "success": False,
                "page_id": page_id,
                "error": str(e)
            }

    async def _retrieve_context(
        self,
        page_content: str,
        primary_keyword: str
    ) -> Dict[str, Any]:
        """Retrieve relevant context via RAG (competitor examples, keyword data)."""
        try:
            query = RetrievalQuery(
                query_text=f"{primary_keyword} meta tags commercial cleaning",
                collection="pages",
                limit=3
            )

            # Retrieve similar pages for reference
            context_pack = self.rag_service.retrieve_context(query)

            return {
                "competitor_examples": context_pack.get("documents", []),
                "keyword_data": {}  # TODO: Fetch from SERP data
            }
        except Exception as e:
            self.logger.warning("context_retrieval_failed", error=str(e))
            return {"competitor_examples": [], "keyword_data": {}}

    async def _execute_optimization(
        self,
        page_content: str,
        current_title: str,
        current_description: str,
        primary_keyword: str,
        secondary_keywords: List[str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute meta optimization prompt template."""

        # Format competitor examples
        competitor_examples = "\n".join([
            f"- Title: {ex.get('title', 'N/A')} | Desc: {ex.get('description', 'N/A')}"
            for ex in context.get("competitor_examples", [])[:3]
        ]) or "No competitor examples available"

        # Prepare inputs
        inputs = {
            "page_content": page_content[:500],  # First 500 chars
            "current_title": current_title,
            "current_description": current_description,
            "primary_keyword": primary_keyword,
            "secondary_keywords": ", ".join(secondary_keywords),
            "competitor_examples": competitor_examples
        }

        # Execute template
        execution = self.prompt_service.execute_template(
            template_name="meta_optimization",
            version="1.0.0",
            inputs=inputs,
            validate=True,
            auto_retry=True
        )

        return execution

    async def _create_change_log(
        self,
        page_id: int,
        page_url: str,
        current_title: str,
        current_description: str,
        new_title: str,
        new_description: str,
        reasoning: str,
        confidence: float,
        all_variants: Dict[str, Any]
    ) -> Any:
        """Create change log entry for governance review."""

        change_id = f"meta_{page_id}_{uuid.uuid4().hex[:8]}"

        change_log = ChangeLogCreate(
            change_id=change_id,
            module=self.MODULE_NAME,
            action="update_meta_tags",
            target_type="wordpress_page",
            target_id=page_id,
            old_value={
                "title": current_title,
                "description": current_description,
                "url": page_url
            },
            new_value={
                "title": new_title,
                "description": new_description,
                "all_variants": all_variants
            },
            reasoning=reasoning,
            ai_confidence=confidence,
            evidence={
                "module": self.MODULE_NAME,
                "timestamp": datetime.utcnow().isoformat(),
                "all_title_variants": all_variants["titles"],
                "all_description_variants": all_variants["descriptions"]
            },
            rollback_ref=None  # TODO: Store backup reference
        )

        # Create via governance API
        result = create_change_log_entry(change_log)
        return result


# Lazy singleton - will be created on first access to avoid initialization errors
# Note: Call get_seo_meta_optimizer() to get the instance instead of using this directly
seo_meta_optimizer = None  # Will be initialized on first access


def get_seo_meta_optimizer() -> SEOMetaOptimizer:
    """Get or create SEO meta optimizer instance."""
    global seo_meta_optimizer
    if seo_meta_optimizer is None:
        seo_meta_optimizer = SEOMetaOptimizer()
    return seo_meta_optimizer
