"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

Prompt Runner Models
Database models for deep research prompts with OpenAI integration
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ResearchPromptTemplate(BaseModel):
    """Research prompt template for deep analysis"""
    id: str
    name: str
    description: str
    template: str
    category: str = "General"
    variables: list[str] = Field(default_factory=list)
    created_by: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class PromptRunConfig(BaseModel):
    """Configuration for a prompt run"""
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    auto_save_to_kb: bool = True


class PromptRun(BaseModel):
    """Record of a prompt execution"""
    id: str
    prompt_id: str
    prompt_name: str
    user_id: int
    input_text: str
    response_text: str
    model: str
    config: PromptRunConfig
    tokens_used: int
    completion_tokens: int
    prompt_tokens: int
    cost_usd: float
    duration_ms: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    saved_to_kb: bool = False
    kb_entry_id: Optional[str] = None
    error: Optional[str] = None
    status: str = "completed"  # pending, running, completed, failed


class KnowledgeBaseEntry(BaseModel):
    """Entry in the knowledge base from prompt responses"""
    id: str
    prompt_run_id: str
    title: str
    content: str
    summary: Optional[str] = None
    category: str = "Research"
    tags: list[str] = Field(default_factory=list)
    embedding: Optional[list[float]] = None  # For vector search
    source_prompt: str
    created_by: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    access_count: int = 0
    last_accessed: Optional[datetime] = None


class PromptRunCreate(BaseModel):
    """Request to run a prompt"""
    prompt_id: str
    input_text: str
    config: Optional[PromptRunConfig] = None


class PromptRunResponse(BaseModel):
    """Response from running a prompt"""
    run_id: str
    response_text: str
    tokens_used: int
    cost_usd: float
    duration_ms: int
    saved_to_kb: bool
    kb_entry_id: Optional[str] = None


class SaveToKnowledgeBaseRequest(BaseModel):
    """Request to save a run to knowledge base"""
    run_id: str
    title: Optional[str] = None
    summary: Optional[str] = None
    tags: list[str] = Field(default_factory=list)


class PromptLibraryStats(BaseModel):
    """Statistics for the prompt library"""
    total_prompts: int
    total_runs: int
    total_kb_entries: int
    total_cost_usd: float
    total_tokens_used: int
    avg_run_duration_ms: float
