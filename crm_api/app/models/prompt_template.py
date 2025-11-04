"""
Copyright (c) 2025 River CityClean
SPDX-License-Identifier: MIT

Prompt Template Data Models

Defines versioned prompt templates with JSON schemas and validation rules.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class OutputType(str, Enum):
    """Canonical output types for AI generation."""
    META_VARIANTS = "meta_variants"
    FAQ_ARRAY = "faq_array"
    JSONLD_SCHEMA = "jsonld_schema"
    INTERNAL_LINK_SUGGESTIONS = "internal_link_suggestions"
    CONTENT_OUTLINE = "content_outline"
    SNIPPET_OPTIMIZATION = "snippet_optimization"
    BACKLINK_PITCH = "backlink_pitch"


class ValidationRule(BaseModel):
    """Single validation rule for outputs."""
    rule_id: str
    rule_type: str  # length, format, json_schema, required_field, etc.
    field_path: str  # JSON path to validate (e.g., "meta_title", "faqs[*].question")
    constraint: Dict[str, Any]  # e.g., {"min": 30, "max": 60}
    error_message: str
    severity: str = "error"  # error, warning


class PromptTemplate(BaseModel):
    """
    Versioned prompt template with validation and retry logic.

    Templates are stored in Qdrant for semantic search.
    """
    template_id: str
    template_name: str
    display_name: str
    description: str

    # Versioning
    version: str = "1.0.0"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    deprecated: bool = False
    superseded_by: Optional[str] = None

    # Template Content
    system_message: str
    user_prompt_template: str
    output_type: OutputType

    # Expected placeholders
    required_placeholders: List[str] = []  # e.g., ["context", "keyword", "url"]

    # Output Schema
    output_schema: Dict[str, Any]  # JSON Schema
    validation_rules: List[ValidationRule] = []

    # Retry Configuration
    max_retries: int = 3
    retry_prompt_template: Optional[str] = None

    # Performance Metrics
    total_uses: int = 0
    successful_generations: int = 0
    failed_generations: int = 0
    avg_retry_count: float = 0.0
    avg_validation_score: float = 0.0

    # Learning
    rejection_feedback: List[Dict[str, Any]] = []
    common_errors: List[Dict[str, int]] = []

    # Metadata
    module_name: str  # e.g., "ctr_optimizer"
    action: str  # e.g., "update_meta_title"
    tags: List[str] = []


class PromptExecution(BaseModel):
    """Record of a single prompt execution."""
    execution_id: str
    template_id: str
    template_version: str

    # Input
    input_variables: Dict[str, Any]
    context_pack_id: Optional[str] = None

    # Execution
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None

    # Retries
    attempt_number: int = 1
    max_attempts: int = 3
    retry_history: List[Dict[str, Any]] = []

    # Output
    raw_output: Optional[str] = None
    parsed_output: Optional[Dict[str, Any]] = None
    validation_passed: bool = False
    validation_errors: List[str] = []

    # Result
    change_log_id: Optional[int] = None
    status: str = "pending"  # pending, success, failed, retrying

    # Learning
    feedback_provided: bool = False
    feedback_reason: Optional[str] = None
    human_rating: Optional[int] = None  # 1-5 stars


class RetryAttempt(BaseModel):
    """Single retry attempt record."""
    attempt_number: int
    timestamp: datetime
    error_type: str
    error_message: str
    retry_prompt_used: str
    raw_output: Optional[str] = None


# ==============================================================================
# Output Schemas (JSON Schema Definitions)
# ==============================================================================

META_VARIANTS_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["meta_title", "meta_description"],
    "properties": {
        "meta_title": {
            "type": "string",
            "minLength": 30,
            "maxLength": 60,
            "description": "Optimized meta title"
        },
        "meta_description": {
            "type": "string",
            "minLength": 120,
            "maxLength": 160,
            "description": "Optimized meta description"
        },
        "variants": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["title", "description"],
                "properties": {
                    "title": {"type": "string", "maxLength": 60},
                    "description": {"type": "string", "maxLength": 160}
                }
            },
            "minItems": 0,
            "maxItems": 3
        },
        "target_keyword": {
            "type": "string"
        },
        "keyword_placement": {
            "type": "object",
            "properties": {
                "title_position": {"type": "integer"},
                "description_position": {"type": "integer"}
            }
        }
    }
}

FAQ_ARRAY_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["faqs"],
    "properties": {
        "faqs": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["question", "answer"],
                "properties": {
                    "question": {
                        "type": "string",
                        "minLength": 10,
                        "maxLength": 200,
                        "description": "FAQ question"
                    },
                    "answer": {
                        "type": "string",
                        "minLength": 50,
                        "maxLength": 500,
                        "description": "FAQ answer"
                    },
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            },
            "minItems": 3,
            "maxItems": 10
        },
        "schema_valid": {
            "type": "boolean",
            "description": "Whether FAQPage schema is valid"
        }
    }
}

JSONLD_SCHEMA_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["@context", "@type"],
    "properties": {
        "@context": {
            "type": "string",
            "const": "https://schema.org"
        },
        "@type": {
            "type": "string",
            "enum": [
                "FAQPage",
                "Article",
                "Product",
                "Organization",
                "LocalBusiness",
                "BreadcrumbList",
                "HowTo"
            ]
        }
    },
    "additionalProperties": True
}

INTERNAL_LINK_SUGGESTIONS_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["suggestions"],
    "properties": {
        "suggestions": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["source_page", "target_page", "anchor_text", "relevance_score"],
                "properties": {
                    "source_page": {
                        "type": "string",
                        "format": "uri"
                    },
                    "target_page": {
                        "type": "string",
                        "format": "uri"
                    },
                    "anchor_text": {
                        "type": "string",
                        "minLength": 2,
                        "maxLength": 100
                    },
                    "context_sentence": {
                        "type": "string",
                        "description": "Sentence where link should be placed"
                    },
                    "relevance_score": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0
                    },
                    "reasoning": {
                        "type": "string"
                    }
                }
            },
            "minItems": 1,
            "maxItems": 10
        }
    }
}

SNIPPET_OPTIMIZATION_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["optimized_snippet", "target_keyword"],
    "properties": {
        "optimized_snippet": {
            "type": "string",
            "minLength": 150,
            "maxLength": 320,
            "description": "Optimized content snippet for SERP"
        },
        "target_keyword": {
            "type": "string"
        },
        "keyword_density": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 5.0
        },
        "readability_score": {
            "type": "number",
            "description": "Flesch reading ease score"
        }
    }
}


# ==============================================================================
# Validation Rules per Output Type
# ==============================================================================

def get_validation_rules(output_type: OutputType) -> List[ValidationRule]:
    """Get validation rules for an output type."""

    rules_map = {
        OutputType.META_VARIANTS: [
            ValidationRule(
                rule_id="meta_title_length",
                rule_type="length",
                field_path="meta_title",
                constraint={"min": 30, "max": 60},
                error_message="Meta title must be 30-60 characters"
            ),
            ValidationRule(
                rule_id="meta_description_length",
                rule_type="length",
                field_path="meta_description",
                constraint={"min": 120, "max": 160},
                error_message="Meta description must be 120-160 characters"
            ),
            ValidationRule(
                rule_id="keyword_in_title",
                rule_type="required_field",
                field_path="target_keyword",
                constraint={"must_appear_in": "meta_title"},
                error_message="Target keyword must appear in meta title"
            )
        ],

        OutputType.FAQ_ARRAY: [
            ValidationRule(
                rule_id="min_faqs",
                rule_type="array_length",
                field_path="faqs",
                constraint={"min": 3, "max": 10},
                error_message="Must have 3-10 FAQs"
            ),
            ValidationRule(
                rule_id="question_length",
                rule_type="length",
                field_path="faqs[*].question",
                constraint={"min": 10, "max": 200},
                error_message="Each question must be 10-200 characters"
            ),
            ValidationRule(
                rule_id="answer_length",
                rule_type="length",
                field_path="faqs[*].answer",
                constraint={"min": 50, "max": 500},
                error_message="Each answer must be 50-500 characters"
            )
        ],

        OutputType.JSONLD_SCHEMA: [
            ValidationRule(
                rule_id="valid_json",
                rule_type="json_schema",
                field_path="$",
                constraint={"schema": JSONLD_SCHEMA_SCHEMA},
                error_message="Must be valid JSON-LD schema"
            ),
            ValidationRule(
                rule_id="required_context",
                rule_type="required_field",
                field_path="@context",
                constraint={"value": "https://schema.org"},
                error_message="@context must be https://schema.org"
            )
        ],

        OutputType.INTERNAL_LINK_SUGGESTIONS: [
            ValidationRule(
                rule_id="valid_urls",
                rule_type="format",
                field_path="suggestions[*].source_page",
                constraint={"format": "uri"},
                error_message="Source page must be valid URL"
            ),
            ValidationRule(
                rule_id="relevance_score_range",
                rule_type="range",
                field_path="suggestions[*].relevance_score",
                constraint={"min": 0.0, "max": 1.0},
                error_message="Relevance score must be 0.0-1.0"
            )
        ]
    }

    return rules_map.get(output_type, [])


# ==============================================================================
# Helper Functions
# ==============================================================================

def get_output_schema(output_type: OutputType) -> Dict[str, Any]:
    """Get JSON schema for an output type."""
    schema_map = {
        OutputType.META_VARIANTS: META_VARIANTS_SCHEMA,
        OutputType.FAQ_ARRAY: FAQ_ARRAY_SCHEMA,
        OutputType.JSONLD_SCHEMA: JSONLD_SCHEMA_SCHEMA,
        OutputType.INTERNAL_LINK_SUGGESTIONS: INTERNAL_LINK_SUGGESTIONS_SCHEMA,
        OutputType.SNIPPET_OPTIMIZATION: SNIPPET_OPTIMIZATION_SCHEMA
    }
    return schema_map.get(output_type, {})
