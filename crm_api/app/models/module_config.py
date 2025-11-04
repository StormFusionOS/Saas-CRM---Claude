"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

Module Configuration Models

Per-module configuration for review vs auto mode, deployment settings,
and rollback policies. This allows gradual graduation from human-review
to automated deployment.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ModuleConfig(BaseModel):
    """
    Configuration for an AI automation module.

    Each AI module (CTR optimizer, anomaly detector, etc.) has its own config
    that controls whether changes require human review or can auto-deploy.
    """
    id: int
    module_name: str = Field(..., description="Unique module identifier (e.g., 'ctr_optimizer')")
    display_name: str = Field(..., description="Human-readable name")

    # Review/Auto Mode Settings
    review_mode: bool = Field(
        default=True,
        description="If true, all suggestions go to pending for human review. If false, can auto-deploy based on confidence."
    )
    auto_deploy_enabled: bool = Field(
        default=False,
        description="If true and review_mode=false, suggestions can deploy automatically"
    )
    auto_deploy_confidence_threshold: float = Field(
        default=0.95,
        description="Minimum confidence score (0.0-1.0) required for auto-deploy"
    )
    auto_deploy_severity_limit: str = Field(
        default="low",
        description="Max severity that can auto-deploy: 'low', 'medium', 'high', 'critical'"
    )

    # Approval Requirements
    approval_required_count: int = Field(
        default=1,
        description="Number of human approvals required (1 or 2)"
    )
    approval_required_roles: Optional[list] = Field(
        default=["admin", "editor"],
        description="Roles allowed to approve changes"
    )

    # Rollback Settings
    rollback_enabled: bool = Field(
        default=True,
        description="If true, executed changes can be reverted"
    )
    auto_rollback_on_error: bool = Field(
        default=False,
        description="If true, automatically revert if execution fails"
    )
    rollback_window_hours: int = Field(
        default=72,
        description="Hours after execution during which rollback is allowed"
    )

    # Rate Limiting
    max_changes_per_day: Optional[int] = Field(
        None,
        description="Maximum suggestions this module can generate per day (None = unlimited)"
    )
    max_pending_changes: Optional[int] = Field(
        10,
        description="Maximum pending suggestions allowed before module pauses"
    )

    # SLA Settings
    review_sla_hours: Optional[int] = Field(
        72,
        description="Hours before a pending change triggers an SLA alert"
    )

    # Module Status
    enabled: bool = Field(
        default=True,
        description="If false, module will not generate new suggestions"
    )
    paused_until: Optional[datetime] = Field(
        None,
        description="If set, module is paused until this datetime"
    )
    pause_reason: Optional[str] = None

    # Graduation Tracking
    graduated_to_auto_at: Optional[datetime] = Field(
        None,
        description="When this module was graduated from review to auto mode"
    )
    graduated_by: Optional[int] = Field(
        None,
        description="User ID who approved graduation to auto mode"
    )

    # Metrics (for graduation decisions)
    total_suggestions: int = Field(default=0)
    total_approved: int = Field(default=0)
    total_rejected: int = Field(default=0)
    total_executed: int = Field(default=0)
    total_failed: int = Field(default=0)
    total_reverted: int = Field(default=0)

    # Audit
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class CreateModuleConfigRequest(BaseModel):
    """Request to create a new module configuration."""
    module_name: str
    display_name: str
    review_mode: bool = True
    auto_deploy_enabled: bool = False
    auto_deploy_confidence_threshold: float = 0.95
    auto_deploy_severity_limit: str = "low"
    approval_required_count: int = 1
    approval_required_roles: Optional[list] = ["admin", "editor"]
    rollback_enabled: bool = True
    max_changes_per_day: Optional[int] = None
    max_pending_changes: Optional[int] = 10
    review_sla_hours: Optional[int] = 72


class UpdateModuleConfigRequest(BaseModel):
    """Request to update module configuration."""
    review_mode: Optional[bool] = None
    auto_deploy_enabled: Optional[bool] = None
    auto_deploy_confidence_threshold: Optional[float] = None
    auto_deploy_severity_limit: Optional[str] = None
    approval_required_count: Optional[int] = None
    enabled: Optional[bool] = None
    paused_until: Optional[datetime] = None
    pause_reason: Optional[str] = None
    max_changes_per_day: Optional[int] = None
    max_pending_changes: Optional[int] = None


class GraduateModuleRequest(BaseModel):
    """Request to graduate module from review to auto mode."""
    auto_deploy_confidence_threshold: float = 0.95
    auto_deploy_severity_limit: str = "low"
    graduation_notes: Optional[str] = None


# In-memory storage (will be replaced with PostgreSQL)
module_configs: Dict[str, ModuleConfig] = {}
_module_config_id_counter = 1


# Initialize default module configurations
DEFAULT_MODULES = [
    {"module_name": "anomaly_detector", "display_name": "Anomaly Detector"},
    {"module_name": "ctr_optimizer", "display_name": "CTR Optimizer"},
    {"module_name": "snippet_optimizer", "display_name": "Featured Snippet Optimizer"},
    {"module_name": "schema_generator", "display_name": "Schema Markup Generator"},
    {"module_name": "content_clusters", "display_name": "Content Cluster Builder"},
    {"module_name": "internal_linking", "display_name": "Internal Linking Assistant"},
    {"module_name": "backlink_finder", "display_name": "Backlink Opportunity Finder"},
    {"module_name": "faq_generator", "display_name": "FAQ Generator"},
    {"module_name": "meta_rewriter", "display_name": "Meta Tag Rewriter"},
    {"module_name": "communications_hub", "display_name": "Communications Hub"},
]


def initialize_default_modules():
    """Initialize module configurations for all AI modules."""
    global _module_config_id_counter

    for module in DEFAULT_MODULES:
        if module["module_name"] not in module_configs:
            config = ModuleConfig(
                id=_module_config_id_counter,
                module_name=module["module_name"],
                display_name=module["display_name"],
                review_mode=True,  # All start in review mode
                auto_deploy_enabled=False,
                enabled=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            module_configs[module["module_name"]] = config
            _module_config_id_counter += 1


# Initialize on module load
initialize_default_modules()
