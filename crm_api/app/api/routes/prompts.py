"""
Copyright (c) 2025 River CityClean
SPDX-License-Identifier: MIT

Prompt Library API Endpoints

Manages versioned prompt templates with validation and execution.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.services.prompt_library import get_prompt_library
from app.models.prompt_template import (
    PromptTemplate,
    PromptExecution,
    OutputType,
    ValidationRule
)
from app.api.deps import require_sales_claims

router = APIRouter(prefix="/prompts", tags=["Prompts"])


# ==============================================================================
# Request/Response Models
# ==============================================================================

class CreateTemplateRequest(BaseModel):
    """Request to create prompt template."""
    template_name: str
    display_name: str
    description: str
    system_message: str
    user_prompt_template: str
    output_type: OutputType
    required_placeholders: List[str] = []
    module_name: str
    action: str
    tags: List[str] = []
    max_retries: int = 3
    retry_prompt_template: Optional[str] = None


class UpdateTemplateRequest(BaseModel):
    """Request to update template."""
    display_name: Optional[str] = None
    description: Optional[str] = None
    system_message: Optional[str] = None
    user_prompt_template: Optional[str] = None
    max_retries: Optional[int] = None


class ExecuteTemplateRequest(BaseModel):
    """Request to execute template."""
    template_id: str
    variables: Dict[str, Any]
    context_pack_id: Optional[str] = None
    mock_output: Optional[str] = None  # For testing without LLM


class AddFeedbackRequest(BaseModel):
    """Request to add feedback to execution."""
    execution_id: str
    feedback_reason: str
    human_rating: Optional[int] = Field(None, ge=1, le=5)


class ValidateOutputRequest(BaseModel):
    """Request to validate output."""
    raw_output: str
    output_type: OutputType


# ==============================================================================
# Template Management Endpoints
# ==============================================================================

@router.post("/templates", response_model=PromptTemplate)
def create_template(
    request: CreateTemplateRequest,
    current_user: dict = Depends(require_sales_claims)
) -> PromptTemplate:
    """
    Create new prompt template.

    Creates a versioned template with JSON schema validation.
    Template will be indexed in Qdrant for semantic search.
    """
    try:
        library = get_prompt_library()

        template = PromptTemplate(
            template_name=request.template_name,
            display_name=request.display_name,
            description=request.description,
            system_message=request.system_message,
            user_prompt_template=request.user_prompt_template,
            output_type=request.output_type,
            required_placeholders=request.required_placeholders,
            module_name=request.module_name,
            action=request.action,
            tags=request.tags,
            max_retries=request.max_retries,
            retry_prompt_template=request.retry_prompt_template,
            output_schema={},  # Will be set by library
            validation_rules=[]  # Will be set by library
        )

        created = library.create_template(template)
        return created

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Template creation failed: {str(e)}")


@router.get("/templates", response_model=List[PromptTemplate])
def list_templates(
    module_name: Optional[str] = None,
    output_type: Optional[OutputType] = None,
    deprecated: bool = False,
    current_user: dict = Depends(require_sales_claims)
) -> List[PromptTemplate]:
    """
    List all prompt templates.

    Filter by module, output type, or deprecated status.
    """
    library = get_prompt_library()
    return library.list_templates(
        module_name=module_name,
        output_type=output_type,
        deprecated=deprecated
    )


@router.get("/templates/{template_id}", response_model=PromptTemplate)
def get_template(
    template_id: str,
    current_user: dict = Depends(require_sales_claims)
) -> PromptTemplate:
    """Get template by ID."""
    library = get_prompt_library()
    template = library.get_template(template_id)

    if not template:
        raise HTTPException(status_code=404, detail=f"Template {template_id} not found")

    return template


@router.put("/templates/{template_id}", response_model=PromptTemplate)
def update_template(
    template_id: str,
    request: UpdateTemplateRequest,
    current_user: dict = Depends(require_sales_claims)
) -> PromptTemplate:
    """
    Update template (creates new version).

    Updates create a new version and deprecate the old one.
    """
    library = get_prompt_library()

    updates = {k: v for k, v in request.model_dump().items() if v is not None}
    updated = library.update_template(template_id, updates)

    if not updated:
        raise HTTPException(status_code=404, detail=f"Template {template_id} not found")

    return updated


@router.delete("/templates/{template_id}")
def deprecate_template(
    template_id: str,
    superseded_by: Optional[str] = None,
    current_user: dict = Depends(require_sales_claims)
) -> Dict[str, Any]:
    """
    Deprecate template.

    Marks template as deprecated. Does not delete.
    """
    library = get_prompt_library()
    success = library.deprecate_template(template_id, superseded_by)

    if not success:
        raise HTTPException(status_code=404, detail=f"Template {template_id} not found")

    return {"status": "deprecated", "template_id": template_id}


# ==============================================================================
# Template Search
# ==============================================================================

@router.get("/templates/search/{query}", response_model=List[PromptTemplate])
def search_templates(
    query: str,
    limit: int = 10,
    module_name: Optional[str] = None,
    current_user: dict = Depends(require_sales_claims)
) -> List[PromptTemplate]:
    """
    Search templates semantically.

    Uses Qdrant vector search to find relevant templates.

    **Example queries:**
    - "optimize meta titles for SEO"
    - "generate FAQ schema"
    - "internal linking suggestions"
    """
    library = get_prompt_library()
    return library.search_templates(
        query=query,
        limit=limit,
        module_name=module_name
    )


# ==============================================================================
# Template Execution
# ==============================================================================

@router.post("/execute", response_model=PromptExecution)
def execute_template(
    request: ExecuteTemplateRequest,
    current_user: dict = Depends(require_sales_claims)
) -> PromptExecution:
    """
    Execute prompt template with validation and retry.

    **Process:**
    1. Fill template with variables
    2. Generate output (currently mock)
    3. Validate against JSON schema
    4. Auto-retry on failure (up to max_retries)
    5. Return execution record

    **Mock Mode:**
    If `mock_output` is provided, it will be used instead of LLM generation.
    This is useful for testing validation without API calls.
    """
    library = get_prompt_library()

    def mock_generate(prompt: str) -> str:
        """Mock generation function."""
        if request.mock_output:
            return request.mock_output
        return '{"meta_title": "Test Title", "meta_description": "Test description for testing purposes only."}'

    try:
        execution = library.execute_template(
            template_id=request.template_id,
            variables=request.variables,
            generate_func=mock_generate,
            context_pack_id=request.context_pack_id
        )

        return execution

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")


# ==============================================================================
# Validation Endpoints
# ==============================================================================

@router.post("/validate", response_model=Dict[str, Any])
def validate_output(
    request: ValidateOutputRequest,
    current_user: dict = Depends(require_sales_claims)
) -> Dict[str, Any]:
    """
    Validate output without executing template.

    Useful for testing outputs before submission.
    """
    from app.services.validation_service import get_validation_service

    validator = get_validation_service()
    is_valid, parsed_output, errors = validator.validate_output(
        raw_output=request.raw_output,
        output_type=request.output_type
    )

    return {
        "is_valid": is_valid,
        "parsed_output": parsed_output,
        "errors": errors
    }


@router.get("/schemas/{output_type}", response_model=Dict[str, Any])
def get_output_schema(
    output_type: OutputType,
    current_user: dict = Depends(require_sales_claims)
) -> Dict[str, Any]:
    """
    Get JSON schema for output type.

    Returns the expected schema for validation.
    """
    from app.models.prompt_template import get_output_schema

    schema = get_output_schema(output_type)
    return schema


@router.get("/rules/{output_type}", response_model=List[ValidationRule])
def get_validation_rules(
    output_type: OutputType,
    current_user: dict = Depends(require_sales_claims)
) -> List[ValidationRule]:
    """
    Get validation rules for output type.

    Returns all rules that will be applied during validation.
    """
    from app.models.prompt_template import get_validation_rules

    rules = get_validation_rules(output_type)
    return rules


# ==============================================================================
# Feedback & Learning
# ==============================================================================

@router.post("/feedback")
def add_feedback(
    request: AddFeedbackRequest,
    current_user: dict = Depends(require_sales_claims)
) -> Dict[str, Any]:
    """
    Add human feedback to execution.

    Feedback is used for nightly learning loop to improve prompts.

    **Rating Scale:**
    - 5: Perfect, no changes needed
    - 4: Good, minor tweaks
    - 3: Acceptable, needs improvement
    - 2: Poor, significant issues
    - 1: Failed, completely wrong
    """
    library = get_prompt_library()

    library.add_feedback(
        execution_id=request.execution_id,
        feedback_reason=request.feedback_reason,
        human_rating=request.human_rating
    )

    return {
        "status": "feedback_recorded",
        "execution_id": request.execution_id
    }


@router.get("/learning-data", response_model=List[Dict[str, Any]])
def get_learning_data(
    template_id: Optional[str] = None,
    min_rating: Optional[int] = None,
    current_user: dict = Depends(require_sales_claims)
) -> List[Dict[str, Any]]:
    """
    Get data for learning loop.

    Returns executions with feedback for prompt improvement.

    **Use Case:**
    Nightly job analyzes feedback to:
    - Identify common failure patterns
    - Optimize prompt templates
    - Adjust validation thresholds
    - Generate better retry prompts
    """
    library = get_prompt_library()
    return library.get_learning_data(
        template_id=template_id,
        min_rating=min_rating
    )


# ==============================================================================
# Statistics
# ==============================================================================

@router.get("/stats/summary", response_model=Dict[str, Any])
def get_summary_stats(
    current_user: dict = Depends(require_sales_claims)
) -> Dict[str, Any]:
    """
    Get prompt library statistics.

    Returns overall metrics across all templates.
    """
    library = get_prompt_library()
    templates = library.list_templates(deprecated=False)

    total_uses = sum(t.total_uses for t in templates)
    total_successful = sum(t.successful_generations for t in templates)
    total_failed = sum(t.failed_generations for t in templates)

    success_rate = (
        (total_successful / total_uses * 100) if total_uses > 0 else 0
    )

    avg_retries = (
        sum(t.avg_retry_count * t.total_uses for t in templates) / total_uses
        if total_uses > 0 else 0
    )

    return {
        "total_templates": len(templates),
        "total_executions": total_uses,
        "successful_executions": total_successful,
        "failed_executions": total_failed,
        "success_rate_pct": round(success_rate, 2),
        "avg_retry_count": round(avg_retries, 2),
        "templates_by_module": _count_by_field(templates, "module_name"),
        "templates_by_output_type": _count_by_field(templates, "output_type")
    }


@router.get("/stats/template/{template_id}", response_model=Dict[str, Any])
def get_template_stats(
    template_id: str,
    current_user: dict = Depends(require_sales_claims)
) -> Dict[str, Any]:
    """
    Get statistics for specific template.

    Includes performance metrics and common errors.
    """
    library = get_prompt_library()
    template = library.get_template(template_id)

    if not template:
        raise HTTPException(status_code=404, detail=f"Template {template_id} not found")

    success_rate = (
        (template.successful_generations / template.total_uses * 100)
        if template.total_uses > 0 else 0
    )

    return {
        "template_id": template_id,
        "template_name": template.template_name,
        "version": template.version,
        "total_uses": template.total_uses,
        "successful": template.successful_generations,
        "failed": template.failed_generations,
        "success_rate_pct": round(success_rate, 2),
        "avg_retry_count": round(template.avg_retry_count, 2),
        "avg_validation_score": round(template.avg_validation_score, 2),
        "feedback_count": len(template.rejection_feedback),
        "common_errors": template.common_errors
    }


def _count_by_field(templates: List[PromptTemplate], field: str) -> Dict[str, int]:
    """Count templates by field value."""
    counts = {}
    for template in templates:
        value = str(getattr(template, field))
        counts[value] = counts.get(value, 0) + 1
    return counts
