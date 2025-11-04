"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

Prompt Runner API Routes
Deep research prompts with OpenAI integration and knowledge base
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import uuid
from datetime import datetime
import time
import structlog

from app.models.prompt_runner import (
    ResearchPromptTemplate,
    PromptRun,
    PromptRunCreate,
    PromptRunResponse,
    PromptRunConfig,
    KnowledgeBaseEntry,
    SaveToKnowledgeBaseRequest,
    PromptLibraryStats,
)
from app.api.deps import require_sales_claims

router = APIRouter(tags=["prompt-runner"])
logger = structlog.get_logger(__name__)

# In-memory storage (will be replaced with database)
_prompt_templates: dict[str, ResearchPromptTemplate] = {}
_prompt_runs: dict[str, PromptRun] = {}
_knowledge_base: dict[str, KnowledgeBaseEntry] = {}

# Initialize with sample templates
def _init_sample_prompts():
    """Initialize with sample prompt templates"""
    samples = [
        ResearchPromptTemplate(
            id=str(uuid.uuid4()),
            name="Competitor Analysis",
            description="Deep analysis of competitor strategies and positioning",
            template="Analyze the following competitor: {{competitor_name}}\n\nFocus on: {{focus_areas}}\n\nProvide insights on their market position, strengths, weaknesses, and strategic direction.",
            category="Market Research",
            variables=["competitor_name", "focus_areas"],
        ),
        ResearchPromptTemplate(
            id=str(uuid.uuid4()),
            name="Market Trends Analysis",
            description="Identify emerging market trends in a specific industry",
            template="Research market trends for: {{industry}}\n\nTime period: {{time_period}}\n\nIdentify key trends, growth opportunities, and potential disruptions.",
            category="Market Research",
            variables=["industry", "time_period"],
        ),
        ResearchPromptTemplate(
            id=str(uuid.uuid4()),
            name="Customer Persona Research",
            description="Build detailed customer personas from market data",
            template="Create a customer persona for: {{business_type}}\n\nTarget market: {{target_market}}\n\nInclude demographics, pain points, motivations, and buying behavior.",
            category="Customer Research",
            variables=["business_type", "target_market"],
        ),
        ResearchPromptTemplate(
            id=str(uuid.uuid4()),
            name="Technology Assessment",
            description="Evaluate emerging technologies for business adoption",
            template="Assess the following technology: {{technology}}\n\nFor use case: {{use_case}}\n\nEvaluate maturity, implementation complexity, ROI potential, and risks.",
            category="Technology",
            variables=["technology", "use_case"],
        ),
    ]
    for prompt in samples:
        _prompt_templates[prompt.id] = prompt

_init_sample_prompts()


# ==============================================================================
# Prompt Templates CRUD
# ==============================================================================

@router.get("/prompt-runner/templates", response_model=List[ResearchPromptTemplate])
def list_prompt_templates(
    category: Optional[str] = None,
    current_user: dict = Depends(require_sales_claims)
):
    """Get list of prompt templates"""
    templates = list(_prompt_templates.values())

    if category:
        templates = [t for t in templates if t.category == category]

    return templates


@router.get("/prompt-runner/templates/{template_id}", response_model=ResearchPromptTemplate)
def get_prompt_template(
    template_id: str,
    current_user: dict = Depends(require_sales_claims)
):
    """Get a specific prompt template"""
    if template_id not in _prompt_templates:
        raise HTTPException(status_code=404, detail="Template not found")
    return _prompt_templates[template_id]


@router.post("/prompt-runner/templates", response_model=ResearchPromptTemplate, status_code=201)
def create_prompt_template(
    template: ResearchPromptTemplate,
    current_user: dict = Depends(require_sales_claims)
):
    """Create a new prompt template"""
    template.id = str(uuid.uuid4())
    template.created_by = current_user.get("user_id")
    template.created_at = datetime.utcnow()
    template.updated_at = datetime.utcnow()

    _prompt_templates[template.id] = template
    logger.info("prompt_template_created", template_id=template.id, name=template.name)

    return template


@router.put("/prompt-runner/templates/{template_id}", response_model=ResearchPromptTemplate)
def update_prompt_template(
    template_id: str,
    updates: ResearchPromptTemplate,
    current_user: dict = Depends(require_sales_claims)
):
    """Update a prompt template"""
    if template_id not in _prompt_templates:
        raise HTTPException(status_code=404, detail="Template not found")

    template = _prompt_templates[template_id]
    template.name = updates.name
    template.description = updates.description
    template.template = updates.template
    template.category = updates.category
    template.variables = updates.variables
    template.updated_at = datetime.utcnow()

    logger.info("prompt_template_updated", template_id=template_id)
    return template


@router.delete("/prompt-runner/templates/{template_id}", status_code=204)
def delete_prompt_template(
    template_id: str,
    current_user: dict = Depends(require_sales_claims)
):
    """Delete a prompt template"""
    if template_id not in _prompt_templates:
        raise HTTPException(status_code=404, detail="Template not found")

    del _prompt_templates[template_id]
    logger.info("prompt_template_deleted", template_id=template_id)


# ==============================================================================
# Prompt Execution
# ==============================================================================

@router.post("/prompt-runner/run", response_model=PromptRunResponse)
async def run_prompt(
    request: PromptRunCreate,
    current_user: dict = Depends(require_sales_claims)
):
    """
    Execute a prompt using OpenAI API

    This is a mock implementation. In production, this would:
    1. Call OpenAI API with the prompt
    2. Track tokens and cost
    3. Store the run in the database
    4. Optionally save to knowledge base
    """
    if request.prompt_id not in _prompt_templates:
        raise HTTPException(status_code=404, detail="Template not found")

    template = _prompt_templates[request.prompt_id]
    config = request.config or PromptRunConfig()

    # Simulate API call timing
    start_time = time.time()

    # Mock OpenAI response (in production, call actual OpenAI API)
    mock_response = f"""Based on your prompt about "{template.name}", here is a comprehensive analysis:

{request.input_text[:200]}...

Key Insights:
1. Market positioning shows strong potential in the target demographic
2. Current trends indicate growing demand for this solution
3. Competitive landscape analysis reveals opportunities for differentiation
4. Technology stack is mature and well-supported
5. Implementation timeline is realistic given current resources

Recommendations:
- Focus on unique value propositions
- Prioritize customer feedback loops
- Monitor competitive movements closely
- Invest in scalable infrastructure
- Build strong partnerships in the ecosystem

This analysis is based on current market data and industry best practices."""

    duration_ms = int((time.time() - start_time) * 1000)

    # Mock token counting (in production, get from OpenAI response)
    prompt_tokens = len(request.input_text.split())
    completion_tokens = len(mock_response.split())
    total_tokens = prompt_tokens + completion_tokens

    # Mock cost calculation (in production, use actual OpenAI pricing)
    cost_per_token = 0.00003 if config.model == "gpt-4" else 0.000002
    cost_usd = total_tokens * cost_per_token

    # Create run record
    run_id = str(uuid.uuid4())
    run = PromptRun(
        id=run_id,
        prompt_id=request.prompt_id,
        prompt_name=template.name,
        user_id=current_user.get("user_id", 1),
        input_text=request.input_text,
        response_text=mock_response,
        model=config.model,
        config=config,
        tokens_used=total_tokens,
        completion_tokens=completion_tokens,
        prompt_tokens=prompt_tokens,
        cost_usd=cost_usd,
        duration_ms=duration_ms,
        status="completed",
    )

    _prompt_runs[run_id] = run

    # Auto-save to knowledge base if configured
    kb_entry_id = None
    if config.auto_save_to_kb:
        kb_entry = KnowledgeBaseEntry(
            id=str(uuid.uuid4()),
            prompt_run_id=run_id,
            title=template.name,
            content=mock_response,
            summary=mock_response[:200] + "...",
            category=template.category,
            tags=[template.category],
            source_prompt=template.name,
            created_by=current_user.get("user_id", 1),
        )
        _knowledge_base[kb_entry.id] = kb_entry
        run.saved_to_kb = True
        run.kb_entry_id = kb_entry.id
        kb_entry_id = kb_entry.id

    logger.info(
        "prompt_executed",
        run_id=run_id,
        template=template.name,
        tokens=total_tokens,
        cost=cost_usd,
        duration_ms=duration_ms,
    )

    return PromptRunResponse(
        run_id=run_id,
        response_text=mock_response,
        tokens_used=total_tokens,
        cost_usd=cost_usd,
        duration_ms=duration_ms,
        saved_to_kb=config.auto_save_to_kb,
        kb_entry_id=kb_entry_id,
    )


# ==============================================================================
# Run History
# ==============================================================================

@router.get("/prompt-runner/runs", response_model=List[PromptRun])
def list_runs(
    limit: int = 100,
    current_user: dict = Depends(require_sales_claims)
):
    """Get list of prompt runs"""
    runs = sorted(
        _prompt_runs.values(),
        key=lambda r: r.created_at,
        reverse=True
    )
    return runs[:limit]


@router.get("/prompt-runner/runs/{run_id}", response_model=PromptRun)
def get_run(
    run_id: str,
    current_user: dict = Depends(require_sales_claims)
):
    """Get a specific run"""
    if run_id not in _prompt_runs:
        raise HTTPException(status_code=404, detail="Run not found")
    return _prompt_runs[run_id]


@router.delete("/prompt-runner/runs/{run_id}", status_code=204)
def delete_run(
    run_id: str,
    current_user: dict = Depends(require_sales_claims)
):
    """Delete a run and its knowledge base entry"""
    if run_id not in _prompt_runs:
        raise HTTPException(status_code=404, detail="Run not found")

    run = _prompt_runs[run_id]

    # Also delete from knowledge base if it was saved there
    if run.saved_to_kb and run.kb_entry_id and run.kb_entry_id in _knowledge_base:
        del _knowledge_base[run.kb_entry_id]
        logger.info("kb_entry_deleted", kb_entry_id=run.kb_entry_id)

    del _prompt_runs[run_id]
    logger.info("prompt_run_deleted", run_id=run_id)


# ==============================================================================
# Knowledge Base
# ==============================================================================

@router.post("/prompt-runner/runs/{run_id}/save-to-kb", response_model=KnowledgeBaseEntry)
def save_run_to_knowledge_base(
    run_id: str,
    request: SaveToKnowledgeBaseRequest,
    current_user: dict = Depends(require_sales_claims)
):
    """Save a run's response to the knowledge base"""
    if run_id not in _prompt_runs:
        raise HTTPException(status_code=404, detail="Run not found")

    run = _prompt_runs[run_id]

    if run.saved_to_kb:
        raise HTTPException(status_code=400, detail="Run already saved to knowledge base")

    template = _prompt_templates.get(run.prompt_id)

    kb_entry = KnowledgeBaseEntry(
        id=str(uuid.uuid4()),
        prompt_run_id=run_id,
        title=request.title or run.prompt_name,
        content=run.response_text,
        summary=request.summary or run.response_text[:200] + "...",
        category=template.category if template else "General",
        tags=request.tags,
        source_prompt=run.prompt_name,
        created_by=current_user.get("user_id", 1),
    )

    _knowledge_base[kb_entry.id] = kb_entry
    run.saved_to_kb = True
    run.kb_entry_id = kb_entry.id

    logger.info("run_saved_to_kb", run_id=run_id, kb_entry_id=kb_entry.id)

    return kb_entry


@router.get("/prompt-runner/knowledge-base", response_model=List[KnowledgeBaseEntry])
def list_knowledge_base(
    category: Optional[str] = None,
    limit: int = 100,
    current_user: dict = Depends(require_sales_claims)
):
    """Get knowledge base entries"""
    entries = list(_knowledge_base.values())

    if category:
        entries = [e for e in entries if e.category == category]

    entries = sorted(entries, key=lambda e: e.created_at, reverse=True)
    return entries[:limit]


@router.get("/prompt-runner/knowledge-base/{entry_id}", response_model=KnowledgeBaseEntry)
def get_knowledge_base_entry(
    entry_id: str,
    current_user: dict = Depends(require_sales_claims)
):
    """Get a specific knowledge base entry"""
    if entry_id not in _knowledge_base:
        raise HTTPException(status_code=404, detail="Entry not found")

    entry = _knowledge_base[entry_id]
    entry.access_count += 1
    entry.last_accessed = datetime.utcnow()

    return entry


@router.delete("/prompt-runner/knowledge-base/{entry_id}", status_code=204)
def delete_knowledge_base_entry(
    entry_id: str,
    current_user: dict = Depends(require_sales_claims)
):
    """Remove an entry from the knowledge base"""
    if entry_id not in _knowledge_base:
        raise HTTPException(status_code=404, detail="Entry not found")

    # Also update the associated run
    for run in _prompt_runs.values():
        if run.kb_entry_id == entry_id:
            run.saved_to_kb = False
            run.kb_entry_id = None
            break

    del _knowledge_base[entry_id]
    logger.info("kb_entry_deleted", entry_id=entry_id)


# ==============================================================================
# Statistics
# ==============================================================================

@router.get("/prompt-runner/stats", response_model=PromptLibraryStats)
def get_stats(current_user: dict = Depends(require_sales_claims)):
    """Get prompt library statistics"""
    runs = list(_prompt_runs.values())

    total_cost = sum(r.cost_usd for r in runs)
    total_tokens = sum(r.tokens_used for r in runs)
    avg_duration = sum(r.duration_ms for r in runs) / len(runs) if runs else 0

    return PromptLibraryStats(
        total_prompts=len(_prompt_templates),
        total_runs=len(runs),
        total_kb_entries=len(_knowledge_base),
        total_cost_usd=total_cost,
        total_tokens_used=total_tokens,
        avg_run_duration_ms=avg_duration,
    )
