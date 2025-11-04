"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Pydantic schemas for Proposal Templates and Assets.

Request/response models for the proposal template API.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# ============================================================================
# Asset Schemas
# ============================================================================


class AssetBase(BaseModel):
    """Base asset model."""

    name: str = Field(..., description="Display name for the asset")
    category: str = Field(default="general", description="Asset category (logo, hero, gallery, general)")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")


class AssetCreate(AssetBase):
    """Schema for creating an asset (used with file upload)."""
    pass


class AssetResponse(AssetBase):
    """Asset response model."""

    id: int
    filename: str
    file_path: str
    file_type: str
    file_size: int
    url: str
    metadata: dict = {}
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# Proposal Template Schemas
# ============================================================================


class ProposalTemplateBase(BaseModel):
    """Base proposal template model."""

    name: str = Field(..., description="Internal name for the template")
    description: str = Field(default="", description="Template description")


class ProposalTemplateCreate(ProposalTemplateBase):
    """Schema for creating a proposal template."""

    brand_logo_asset_id: Optional[int] = Field(None, description="ID of brand logo asset")
    brand_primary_color: str = Field(default="#0066cc", description="Primary brand color (hex)")
    brand_secondary_color: str = Field(default="#003366", description="Secondary brand color (hex)")
    hero_image_asset_id: Optional[int] = Field(None, description="ID of hero image asset")

    header_html: str = Field(default="", description="Header section HTML")
    introduction_html: str = Field(default="", description="Introduction section HTML")
    services_section_html: str = Field(default="", description="Services list HTML")
    benefits_html: str = Field(default="", description="Benefits section HTML")
    scope_html: str = Field(default="", description="Scope of work HTML")
    exclusions_html: str = Field(default="", description="Exclusions section HTML")
    terms_html: str = Field(default="", description="Terms and conditions HTML")
    footer_html: str = Field(default="", description="Footer section HTML")

    gallery_asset_ids: List[int] = Field(default_factory=list, description="Gallery asset IDs")
    service_categories: List[str] = Field(default_factory=list, description="Applicable service categories")
    package_tiers: List[str] = Field(default_factory=list, description="Applicable package tiers")

    is_default: bool = Field(default=False, description="Use as default template")
    is_active: bool = Field(default=True, description="Template is active")
    display_order: int = Field(default=0, description="Display order")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")


class ProposalTemplateUpdate(BaseModel):
    """Schema for updating a proposal template."""

    name: Optional[str] = None
    description: Optional[str] = None
    brand_logo_asset_id: Optional[int] = None
    brand_primary_color: Optional[str] = None
    brand_secondary_color: Optional[str] = None
    hero_image_asset_id: Optional[int] = None
    header_html: Optional[str] = None
    introduction_html: Optional[str] = None
    services_section_html: Optional[str] = None
    benefits_html: Optional[str] = None
    scope_html: Optional[str] = None
    exclusions_html: Optional[str] = None
    terms_html: Optional[str] = None
    footer_html: Optional[str] = None
    gallery_asset_ids: Optional[List[int]] = None
    service_categories: Optional[List[str]] = None
    package_tiers: Optional[List[str]] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None
    metadata: Optional[dict] = None


class ProposalTemplateResponse(ProposalTemplateBase):
    """Proposal template response model."""

    id: int
    brand_logo_asset_id: Optional[int]
    brand_primary_color: str
    brand_secondary_color: str
    hero_image_asset_id: Optional[int]
    header_html: str
    introduction_html: str
    services_section_html: str
    benefits_html: str
    scope_html: str
    exclusions_html: str
    terms_html: str
    footer_html: str
    gallery_asset_ids: List[int]
    service_categories: List[str]
    package_tiers: List[str]
    is_default: bool
    is_active: bool
    display_order: int
    available_tokens: List[str]
    metadata: dict
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProposalTemplateListItem(BaseModel):
    """Minimal template model for list views."""

    id: int
    name: str
    description: str
    is_default: bool
    is_active: bool
    service_categories: List[str]
    package_tiers: List[str]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# Proposal Rendering Schemas
# ============================================================================


class ProposalRenderRequest(BaseModel):
    """Request to render a proposal for a quote."""

    quote_id: int = Field(..., description="Quote ID to render")
    template_id: Optional[int] = Field(None, description="Template ID (uses default if not specified)")


class ProposalRenderResponse(BaseModel):
    """Rendered proposal response."""

    html: str = Field(..., description="Rendered HTML content")
    quote_id: int
    template_id: int
    preview_url: str = Field(..., description="URL to view the proposal")


class ProposalPreviewResponse(BaseModel):
    """Preview of a template with sample data."""

    html: str = Field(..., description="Rendered HTML with sample data")
    template_id: int


# ============================================================================
# Quote Acceptance Schemas
# ============================================================================


class QuoteAcceptanceRequest(BaseModel):
    """Request to accept a quote."""

    signature_name: str = Field(..., min_length=2, max_length=100, description="Full name for signature")
    terms_accepted: bool = Field(..., description="Must be True to accept")
    initialed_clauses: dict = Field(default_factory=dict, description="Clause IDs mapped to initials")

    class Config:
        json_schema_extra = {
            "example": {
                "signature_name": "John Smith",
                "terms_accepted": True,
                "initialed_clauses": {
                    "ladder_waiver": "JS",
                    "oxidation_disclaimer": "JS"
                }
            }
        }


class QuoteAcceptanceResponse(BaseModel):
    """Response after accepting a quote."""

    quote_id: int
    quote_number: str
    status: str
    accepted_at: datetime
    signature_name: str
    message: str = Field(..., description="Success message")
    pdf_url: Optional[str] = Field(None, description="URL to download accepted proposal PDF")
