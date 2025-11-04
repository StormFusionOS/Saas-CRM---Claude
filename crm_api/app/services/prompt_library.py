"""
Copyright (c) 2025 River CityClean
SPDX-License-Identifier: MIT

Prompt Library Service

Manages versioned prompt templates with semantic search capabilities.
Integrates with Qdrant for prompt discovery and validation service for quality.
"""

from typing import List, Dict, Any, Optional
import uuid
import structlog
from datetime import datetime

from app.services.qdrant_service import QdrantService, COLLECTION_PROMPT_LIBRARY
from app.services.embedding_service import get_embedding_service
from app.services.validation_service import get_validation_service
from app.models.prompt_template import (
    PromptTemplate,
    PromptExecution,
    RetryAttempt,
    OutputType,
    get_output_schema,
    get_validation_rules
)

logger = structlog.get_logger(__name__)


# ==============================================================================
# In-Memory Storage (Replace with PostgreSQL later)
# ==============================================================================

prompt_templates: Dict[str, PromptTemplate] = {}
prompt_executions: Dict[str, PromptExecution] = {}


class PromptLibraryService:
    """
    Service for managing and executing prompt templates.

    Features:
    - Versioned templates
    - Semantic search
    - Validation + auto-retry
    - Learning from feedback
    """

    def __init__(
        self,
        qdrant_service: Optional[QdrantService] = None
    ):
        """Initialize prompt library service."""
        self.qdrant = qdrant_service
        self.embeddings = get_embedding_service()
        self.validator = get_validation_service()
        self.logger = logger.bind(service="prompt_library")

    # ==========================================================================
    # Template Management
    # ==========================================================================

    def create_template(self, template: PromptTemplate) -> PromptTemplate:
        """
        Create new prompt template.

        Args:
            template: Template to create

        Returns:
            Created template
        """
        template.template_id = str(uuid.uuid4())
        template.created_at = datetime.now()
        template.updated_at = datetime.now()

        # Store in memory
        prompt_templates[template.template_id] = template

        # Store embedding in Qdrant if available
        if self.qdrant:
            self._index_template(template)

        self.logger.info(
            "template_created",
            template_id=template.template_id,
            template_name=template.template_name,
            version=template.version
        )

        return template

    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Get template by ID."""
        return prompt_templates.get(template_id)

    def list_templates(
        self,
        module_name: Optional[str] = None,
        output_type: Optional[OutputType] = None,
        deprecated: bool = False
    ) -> List[PromptTemplate]:
        """
        List templates with optional filters.

        Args:
            module_name: Filter by module
            output_type: Filter by output type
            deprecated: Include deprecated templates

        Returns:
            List of templates
        """
        templates = list(prompt_templates.values())

        if module_name:
            templates = [t for t in templates if t.module_name == module_name]

        if output_type:
            templates = [t for t in templates if t.output_type == output_type]

        if not deprecated:
            templates = [t for t in templates if not t.deprecated]

        return templates

    def update_template(
        self,
        template_id: str,
        updates: Dict[str, Any]
    ) -> Optional[PromptTemplate]:
        """Update template (creates new version)."""
        template = self.get_template(template_id)
        if not template:
            return None

        # Increment version
        major, minor, patch = template.version.split(".")
        new_version = f"{major}.{int(minor) + 1}.0"

        # Create new template with updates
        template_dict = template.model_dump()
        template_dict.update(updates)
        template_dict["version"] = new_version
        template_dict["updated_at"] = datetime.now()

        new_template = PromptTemplate(**template_dict)
        return self.create_template(new_template)

    def deprecate_template(
        self,
        template_id: str,
        superseded_by: Optional[str] = None
    ) -> bool:
        """Mark template as deprecated."""
        template = self.get_template(template_id)
        if not template:
            return False

        template.deprecated = True
        template.superseded_by = superseded_by
        template.updated_at = datetime.now()

        return True

    # ==========================================================================
    # Semantic Search
    # ==========================================================================

    def _index_template(self, template: PromptTemplate):
        """Index template in Qdrant for semantic search."""
        if not self.qdrant:
            return

        # Combine searchable text
        searchable_text = f"{template.display_name} {template.description} {template.user_prompt_template}"
        embedding = self.embeddings.embed_text(searchable_text)

        # Store in Qdrant
        self.qdrant.upsert_embedding(
            collection_name=COLLECTION_PROMPT_LIBRARY,
            point_id=template.template_id,
            embedding=embedding,
            payload={
                "template_id": template.template_id,
                "template_name": template.template_name,
                "display_name": template.display_name,
                "description": template.description,
                "module_name": template.module_name,
                "action": template.action,
                "output_type": template.output_type.value,
                "version": template.version,
                "deprecated": template.deprecated
            }
        )

    def search_templates(
        self,
        query: str,
        limit: int = 10,
        module_name: Optional[str] = None
    ) -> List[PromptTemplate]:
        """
        Search templates semantically.

        Args:
            query: Search query
            limit: Max results
            module_name: Optional module filter

        Returns:
            Matching templates
        """
        if not self.qdrant:
            return []

        # Generate query embedding
        query_embedding = self.embeddings.embed_text(query)

        # Search
        filters = {}
        if module_name:
            filters["module_name"] = module_name

        results = self.qdrant.search_similar(
            collection_name=COLLECTION_PROMPT_LIBRARY,
            query_embedding=query_embedding,
            limit=limit,
            filter_conditions=filters
        )

        # Fetch full templates
        template_ids = [r["payload"]["template_id"] for r in results]
        return [self.get_template(tid) for tid in template_ids if self.get_template(tid)]

    # ==========================================================================
    # Template Execution
    # ==========================================================================

    def execute_template(
        self,
        template_id: str,
        variables: Dict[str, Any],
        generate_func,
        context_pack_id: Optional[str] = None,
        max_retries: Optional[int] = None
    ) -> PromptExecution:
        """
        Execute prompt template with validation and retry.

        Args:
            template_id: Template to execute
            variables: Variables to fill in template
            generate_func: Function that generates output (callable)
            context_pack_id: Associated context pack
            max_retries: Max retry attempts (defaults to template setting)

        Returns:
            Execution record
        """
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")

        # Create execution record
        execution = PromptExecution(
            execution_id=str(uuid.uuid4()),
            template_id=template_id,
            template_version=template.version,
            input_variables=variables,
            context_pack_id=context_pack_id,
            started_at=datetime.now(),
            max_attempts=max_retries or template.max_retries
        )

        # Fill in template
        prompt = self._fill_template(template.user_prompt_template, variables)

        # Execute with retry
        success, parsed_output, errors, attempts = self.validator.validate_with_retry(
            generate_func=generate_func,
            prompt=prompt,
            output_type=template.output_type,
            max_retries=execution.max_attempts
        )

        # Update execution
        execution.completed_at = datetime.now()
        execution.duration_seconds = (
            execution.completed_at - execution.started_at
        ).total_seconds()
        execution.attempt_number = attempts
        execution.validation_passed = success
        execution.validation_errors = errors
        execution.status = "success" if success else "failed"

        if success:
            execution.parsed_output = parsed_output

        # Update template metrics
        template.total_uses += 1
        if success:
            template.successful_generations += 1
        else:
            template.failed_generations += 1

        template.avg_retry_count = (
            (template.avg_retry_count * (template.total_uses - 1) + attempts) /
            template.total_uses
        )

        # Store execution
        prompt_executions[execution.execution_id] = execution

        self.logger.info(
            "template_executed",
            execution_id=execution.execution_id,
            template_id=template_id,
            success=success,
            attempts=attempts
        )

        return execution

    def _fill_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Fill template with variables."""
        filled = template
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            filled = filled.replace(placeholder, str(value))
        return filled

    # ==========================================================================
    # Feedback & Learning
    # ==========================================================================

    def add_feedback(
        self,
        execution_id: str,
        feedback_reason: str,
        human_rating: Optional[int] = None
    ):
        """
        Add human feedback to execution.

        Used for nightly learning loop.

        Args:
            execution_id: Execution to provide feedback on
            feedback_reason: Why approved/rejected
            human_rating: 1-5 star rating
        """
        execution = prompt_executions.get(execution_id)
        if not execution:
            return

        execution.feedback_provided = True
        execution.feedback_reason = feedback_reason
        execution.human_rating = human_rating

        # Add to template rejection feedback
        template = self.get_template(execution.template_id)
        if template:
            template.rejection_feedback.append({
                "execution_id": execution_id,
                "timestamp": datetime.now().isoformat(),
                "reason": feedback_reason,
                "rating": human_rating,
                "variables": execution.input_variables
            })

    def get_learning_data(
        self,
        template_id: Optional[str] = None,
        min_rating: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get data for learning loop.

        Args:
            template_id: Optional template filter
            min_rating: Minimum rating filter

        Returns:
            List of feedback data
        """
        executions = list(prompt_executions.values())

        if template_id:
            executions = [e for e in executions if e.template_id == template_id]

        if min_rating:
            executions = [
                e for e in executions
                if e.human_rating and e.human_rating >= min_rating
            ]

        return [
            {
                "execution_id": e.execution_id,
                "template_id": e.template_id,
                "template_version": e.template_version,
                "success": e.validation_passed,
                "attempts": e.attempt_number,
                "rating": e.human_rating,
                "feedback": e.feedback_reason,
                "variables": e.input_variables,
                "output": e.parsed_output
            }
            for e in executions
            if e.feedback_provided
        ]


# ==============================================================================
# Default Prompt Templates
# ==============================================================================

DEFAULT_TEMPLATES = [
    {
        "template_name": "meta_title_optimizer",
        "display_name": "Meta Title Optimizer",
        "description": "Generate optimized meta titles for SEO",
        "system_message": "You are an SEO expert specializing in meta title optimization.",
        "user_prompt_template": """
Based on the following context:

{context}

Generate an optimized meta title for the page: {url}

Requirements:
- Target keyword: {keyword}
- 50-60 characters
- Include keyword naturally
- Compelling and click-worthy
- Unique from competitors

Return JSON format:
{
  "meta_title": "Your optimized title here",
  "meta_description": "Your optimized description here",
  "target_keyword": "{keyword}"
}
""",
        "output_type": OutputType.META_VARIANTS,
        "required_placeholders": ["context", "url", "keyword"],
        "module_name": "ctr_optimizer",
        "action": "update_meta_title",
        "tags": ["seo", "meta", "ctr"],
        "retry_prompt_template": """
Your previous meta title had errors. Please fix and regenerate.

Ensure:
- 50-60 characters (you provided {actual_length})
- Keyword "{keyword}" is included
- Valid JSON format
"""
    },

    {
        "template_name": "faq_generator",
        "display_name": "FAQ Schema Generator",
        "description": "Generate FAQ schema markup from page content",
        "system_message": "You are an expert in structured data and FAQ schema generation.",
        "user_prompt_template": """
Based on this page content:

{context}

Generate 5-7 frequently asked questions related to: {keyword}

Requirements:
- Questions should be natural and conversational
- Answers should be 50-150 words
- Based on page content and SERP PAA
- Valid for FAQPage schema

Return JSON format:
{
  "faqs": [
    {"question": "...", "answer": "..."},
    ...
  ]
}
""",
        "output_type": OutputType.FAQ_ARRAY,
        "required_placeholders": ["context", "keyword"],
        "module_name": "schema_generator",
        "action": "generate_faq_schema",
        "tags": ["schema", "faq", "structured-data"]
    },

    {
        "template_name": "internal_link_suggester",
        "display_name": "Internal Link Suggester",
        "description": "Suggest relevant internal links for a page",
        "system_message": "You are an internal linking expert. Suggest contextually relevant internal links.",
        "user_prompt_template": """
Source page: {url}
Target keyword: {keyword}

Available pages to link to:
{context}

Suggest 3-5 internal links that would be most relevant.

Return JSON format:
{
  "suggestions": [
    {
      "source_page": "{url}",
      "target_page": "URL",
      "anchor_text": "Natural anchor text",
      "context_sentence": "Sentence where link should be placed",
      "relevance_score": 0.95,
      "reasoning": "Why this link is relevant"
    }
  ]
}
""",
        "output_type": OutputType.INTERNAL_LINK_SUGGESTIONS,
        "required_placeholders": ["url", "keyword", "context"],
        "module_name": "internal_linking",
        "action": "suggest_internal_links",
        "tags": ["internal-linking", "seo"]
    }
]


def initialize_default_templates(library: PromptLibraryService):
    """Initialize default prompt templates."""
    for template_data in DEFAULT_TEMPLATES:
        template_data["output_schema"] = get_output_schema(template_data["output_type"])
        template_data["validation_rules"] = get_validation_rules(template_data["output_type"])

        template = PromptTemplate(**template_data)
        library.create_template(template)

    logger.info("default_templates_initialized", count=len(DEFAULT_TEMPLATES))


# ==============================================================================
# Singleton Instance
# ==============================================================================

_prompt_library: Optional[PromptLibraryService] = None


def get_prompt_library(
    qdrant_service: Optional[QdrantService] = None
) -> PromptLibraryService:
    """Get or create prompt library instance."""
    global _prompt_library

    if _prompt_library is None:
        _prompt_library = PromptLibraryService(qdrant_service=qdrant_service)
        initialize_default_templates(_prompt_library)

    return _prompt_library


# Lazy singleton - will be created on first access
# Note: Import get_prompt_library() and call it instead of using this directly
# to avoid initialization errors at import time
prompt_library_service = None  # Will be initialized on first access via get_prompt_library()
