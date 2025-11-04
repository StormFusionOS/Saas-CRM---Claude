"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Proposal Templates and Assets API Routes - Sales Suite

All proposal template and asset management endpoints.
Must be mounted under /sales/... to ensure proper Sales Suite scoping.
"""

import os
import uuid
from typing import List, Optional
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    UploadFile,
    File,
    Form,
    status,
    Request,
)
from fastapi.responses import HTMLResponse, FileResponse
from app.db import get_db, InMemoryDB
from app.api.deps import require_sales_claims
from app.schemas.proposals import (
    AssetCreate,
    AssetResponse,
    ProposalTemplateCreate,
    ProposalTemplateUpdate,
    ProposalTemplateResponse,
    ProposalTemplateListItem,
    ProposalRenderResponse,
    ProposalPreviewResponse,
    QuoteAcceptanceRequest,
    QuoteAcceptanceResponse,
)
from app.services import proposal_service


router = APIRouter(tags=["sales", "proposals"])


# ============================================================================
# Asset Endpoints
# ============================================================================


@router.post("/assets", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def upload_asset(
    file: UploadFile = File(...),
    name: str = Form(...),
    category: str = Form(default="general"),
    tags: Optional[str] = Form(default=None),  # Comma-separated string
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims),
) -> AssetResponse:
    """
    Upload an asset file.

    Upload images, logos, or other files for use in proposal templates.

    **Sales Suite Access Only** - Requires sales role claims.

    Args:
        file: File to upload
        name: Display name for the asset
        category: Asset category (logo, hero, gallery, general)
        tags: Comma-separated tags
        db: Database session
        claims: JWT claims with sales permissions

    Returns:
        Created asset with URL

    Raises:
        HTTPException: If file type not supported or upload fails
    """
    # Validate file type
    allowed_types = [
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/gif",
        "image/webp",
        "application/pdf",
    ]

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file.content_type} not supported. Allowed: {', '.join(allowed_types)}",
        )

    # Create assets directory if it doesn't exist
    assets_dir = "/tmp/sales_suite_assets"
    os.makedirs(assets_dir, exist_ok=True)

    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(assets_dir, unique_filename)

    # Save file
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}",
        )

    # Parse tags
    tag_list = [t.strip() for t in tags.split(",")] if tags else []

    # Create asset record
    asset = proposal_service.create_asset(
        db=db,
        name=name,
        filename=file.filename,
        file_path=file_path,
        file_type=file.content_type,
        file_size=len(contents),
        url=f"/api/v1/sales/assets/{unique_filename}",
        category=category,
        tags=tag_list,
    )

    return AssetResponse.model_validate(asset)


@router.get("/assets", response_model=List[AssetResponse])
def list_assets(
    category: Optional[str] = Query(None, description="Filter by category"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims),
) -> List[AssetResponse]:
    """
    List all assets.

    Get list of uploaded assets with optional filtering.

    **Sales Suite Access Only** - Requires sales role claims.

    Args:
        category: Filter by category
        tags: Filter by tags (comma-separated)
        db: Database session
        claims: JWT claims

    Returns:
        List of assets
    """
    tag_list = [t.strip() for t in tags.split(",")] if tags else None

    assets = proposal_service.list_assets(
        db=db,
        category=category,
        tags=tag_list,
    )

    return [AssetResponse.model_validate(a) for a in assets]


@router.get("/assets/{asset_id}", response_model=AssetResponse)
def get_asset(
    asset_id: int,
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims),
) -> AssetResponse:
    """
    Get asset by ID.

    **Sales Suite Access Only** - Requires sales role claims.

    Args:
        asset_id: Asset ID
        db: Database session
        claims: JWT claims

    Returns:
        Asset details

    Raises:
        HTTPException: If asset not found
    """
    asset = proposal_service.get_asset(db, asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset {asset_id} not found",
        )

    return AssetResponse.model_validate(asset)


@router.delete("/assets/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(
    asset_id: int,
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims),
):
    """
    Delete an asset.

    Deletes both the database record and the physical file.

    **Sales Suite Access Only** - Requires sales role claims.

    Args:
        asset_id: Asset ID to delete
        db: Database session
        claims: JWT claims

    Raises:
        HTTPException: If asset not found
    """
    success = proposal_service.delete_asset(db, asset_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset {asset_id} not found",
        )


# ============================================================================
# Proposal Template Endpoints
# ============================================================================


@router.post("/templates", response_model=ProposalTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_template(
    template_data: ProposalTemplateCreate,
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims),
) -> ProposalTemplateResponse:
    """
    Create a new proposal template.

    Create a template with branding, content sections, and tokenized variables.

    **Sales Suite Access Only** - Requires sales role claims.

    Args:
        template_data: Template creation data
        db: Database session
        claims: JWT claims

    Returns:
        Created template

    Raises:
        HTTPException: If referenced assets don't exist
    """
    # Validate asset IDs exist
    if template_data.brand_logo_asset_id:
        asset = proposal_service.get_asset(db, template_data.brand_logo_asset_id)
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Brand logo asset {template_data.brand_logo_asset_id} not found",
            )

    if template_data.hero_image_asset_id:
        asset = proposal_service.get_asset(db, template_data.hero_image_asset_id)
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hero image asset {template_data.hero_image_asset_id} not found",
            )

    # Create template
    template = proposal_service.create_template(
        db=db,
        **template_data.model_dump(),
    )

    return ProposalTemplateResponse.model_validate(template)


@router.get("/templates", response_model=List[ProposalTemplateListItem])
def list_templates(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    service_category: Optional[str] = Query(None, description="Filter by service category"),
    package_tier: Optional[str] = Query(None, description="Filter by package tier"),
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims),
) -> List[ProposalTemplateListItem]:
    """
    List all proposal templates.

    Get list of templates with optional filtering.

    **Sales Suite Access Only** - Requires sales role claims.

    Args:
        is_active: Filter by active status
        service_category: Filter by service category
        package_tier: Filter by package tier
        db: Database session
        claims: JWT claims

    Returns:
        List of templates
    """
    templates = proposal_service.list_templates(
        db=db,
        is_active=is_active,
        service_category=service_category,
        package_tier=package_tier,
    )

    return [ProposalTemplateListItem.model_validate(t) for t in templates]


@router.get("/templates/{template_id}", response_model=ProposalTemplateResponse)
def get_template(
    template_id: int,
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims),
) -> ProposalTemplateResponse:
    """
    Get template by ID.

    **Sales Suite Access Only** - Requires sales role claims.

    Args:
        template_id: Template ID
        db: Database session
        claims: JWT claims

    Returns:
        Template details

    Raises:
        HTTPException: If template not found
    """
    template = proposal_service.get_template(db, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template {template_id} not found",
        )

    return ProposalTemplateResponse.model_validate(template)


@router.patch("/templates/{template_id}", response_model=ProposalTemplateResponse)
def update_template(
    template_id: int,
    template_data: ProposalTemplateUpdate,
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims),
) -> ProposalTemplateResponse:
    """
    Update a proposal template.

    Update template content, branding, or settings.

    **Sales Suite Access Only** - Requires sales role claims.

    Args:
        template_id: Template ID to update
        template_data: Fields to update
        db: Database session
        claims: JWT claims

    Returns:
        Updated template

    Raises:
        HTTPException: If template not found
    """
    # Only include fields that were explicitly set
    updates = template_data.model_dump(exclude_unset=True)

    template = proposal_service.update_template(db, template_id, **updates)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template {template_id} not found",
        )

    return ProposalTemplateResponse.model_validate(template)


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(
    template_id: int,
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims),
):
    """
    Delete a proposal template.

    **Sales Suite Access Only** - Requires sales role claims.

    Args:
        template_id: Template ID to delete
        db: Database session
        claims: JWT claims

    Raises:
        HTTPException: If template not found
    """
    success = proposal_service.delete_template(db, template_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template {template_id} not found",
        )


# ============================================================================
# Proposal Rendering Endpoints
# ============================================================================


@router.get("/proposals/{quote_id}/preview", response_class=HTMLResponse)
def preview_proposal(
    quote_id: int,
    template_id: Optional[int] = Query(None, description="Template ID (uses default if not specified)"),
    db: InMemoryDB = Depends(get_db),
    claims: dict = Depends(require_sales_claims),
) -> str:
    """
    Preview a proposal for a quote (internal use).

    Renders a proposal using the specified template (or default).

    **Sales Suite Access Only** - Requires sales role claims.

    Args:
        quote_id: Quote ID
        template_id: Optional template ID
        db: Database session
        claims: JWT claims

    Returns:
        Rendered HTML

    Raises:
        HTTPException: If quote or template not found
    """
    # Get quote
    quote = db.quotes.get(quote_id)
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quote {quote_id} not found",
        )

    # Get template
    template = None
    if template_id:
        template = proposal_service.get_template(db, template_id)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template {template_id} not found",
            )

    # Render proposal
    html = proposal_service.render_proposal(db, quote, template)
    return html


# Public endpoint (no auth required) for customer-facing proposals
@router.get("/proposals/{quote_id}/public", response_class=HTMLResponse, include_in_schema=False)
def view_public_proposal(
    quote_id: int,
    db: InMemoryDB = Depends(get_db),
) -> str:
    """
    View public proposal (customer-facing).

    This is the URL customers receive to view their proposal.
    No authentication required.

    Args:
        quote_id: Quote ID
        db: Database session

    Returns:
        Rendered HTML

    Raises:
        HTTPException: If quote not found or not sent yet
    """
    # Get quote
    quote = db.quotes.get(quote_id)
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found",
        )

    # Only allow viewing if quote has been sent
    if not quote.sent_at:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This proposal has not been sent yet",
        )

    # Get template (use the one assigned to quote, or default)
    template = None
    if quote.proposal_template_id:
        template = proposal_service.get_template(db, quote.proposal_template_id)

    # Render proposal
    html = proposal_service.render_proposal(db, quote, template)

    # Track view (update viewed_at timestamp)
    if not quote.viewed_at:
        from datetime import datetime
        quote.viewed_at = datetime.utcnow()
        if quote.status == "SENT":
            quote.status = "VIEWED"

    return html


# ============================================================================
# Quote Acceptance Endpoint
# ============================================================================


@router.post("/proposals/{quote_id}/accept", response_model=QuoteAcceptanceResponse, include_in_schema=False)
def accept_quote(
    quote_id: int,
    acceptance_data: QuoteAcceptanceRequest,
    request: Request,
    db: InMemoryDB = Depends(get_db),
) -> QuoteAcceptanceResponse:
    """
    Accept a quote (e-signature).

    Customer endpoint to accept a proposal with signature.
    No authentication required - this is the public acceptance endpoint.

    Args:
        quote_id: Quote ID
        acceptance_data: Acceptance request with signature name, terms acceptance, and initials
        request: FastAPI request object (for IP/user agent extraction)
        db: Database session

    Returns:
        Acceptance confirmation with quote details

    Raises:
        HTTPException: If quote not found, already accepted, or validation fails
    """
    from datetime import datetime
    from app.models import Quote

    # Get quote
    quote = db.query(Quote).filter_by(id=quote_id).first()
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found",
        )

    # Validate quote status - can only accept if SENT or VIEWED
    if quote.status not in ["SENT", "VIEWED"]:
        if quote.status == "ACCEPTED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This proposal has already been accepted",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Proposal cannot be accepted in {quote.status} status",
        )

    # Validate terms were accepted
    if not acceptance_data.terms_accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must accept the terms and conditions",
        )

    # Validate required initialed clauses (if template has them)
    template = None
    if quote.proposal_template_id:
        template = proposal_service.get_template(db, quote.proposal_template_id)
        if template and template.initialed_clauses:
            required_clauses = [c for c in template.initialed_clauses if c.get("required", False)]
            for clause in required_clauses:
                clause_id = clause.get("id")
                if not clause_id or clause_id not in acceptance_data.initialed_clauses:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"You must initial the required clause: {clause.get('title', clause_id)}",
                    )

    # Extract IP address and user agent
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    # Update quote with acceptance data
    quote.status = "ACCEPTED"
    quote.accepted_at = datetime.utcnow()
    quote.signature_name = acceptance_data.signature_name
    quote.signature_ip = client_ip
    quote.signature_user_agent = user_agent
    quote.terms_accepted = True
    quote.initialed_clauses = acceptance_data.initialed_clauses
    quote.updated_at = datetime.utcnow()

    # Generate PDF URL (placeholder for now - would implement actual PDF generation)
    pdf_url = f"/api/v1/sales/proposals/{quote_id}/pdf"

    return QuoteAcceptanceResponse(
        quote_id=quote.id,
        quote_number=quote.quote_number,
        status=quote.status,
        accepted_at=quote.accepted_at,
        signature_name=quote.signature_name,
        message=f"Thank you! Your proposal {quote.quote_number} has been accepted.",
        pdf_url=pdf_url,
    )
