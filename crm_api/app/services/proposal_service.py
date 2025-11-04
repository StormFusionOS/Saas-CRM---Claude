"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Proposal Template and Asset Service.

Business logic for managing proposal templates and assets.
"""

import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.models import (
    ProposalTemplate,
    Asset,
    Quote,
    get_next_proposal_template_id,
    get_next_asset_id,
)
from app.db import InMemoryDB


def create_template(
    db: InMemoryDB,
    name: str,
    description: str = "",
    brand_logo_asset_id: Optional[int] = None,
    brand_primary_color: str = "#0066cc",
    brand_secondary_color: str = "#003366",
    hero_image_asset_id: Optional[int] = None,
    header_html: str = "",
    introduction_html: str = "",
    services_section_html: str = "",
    benefits_html: str = "",
    scope_html: str = "",
    exclusions_html: str = "",
    terms_html: str = "",
    footer_html: str = "",
    gallery_asset_ids: Optional[List[int]] = None,
    service_categories: Optional[List[str]] = None,
    package_tiers: Optional[List[str]] = None,
    is_default: bool = False,
    is_active: bool = True,
    **kwargs
) -> ProposalTemplate:
    """Create a new proposal template."""

    template_id = get_next_proposal_template_id()

    template = ProposalTemplate(
        id=template_id,
        name=name,
        description=description,
        brand_logo_asset_id=brand_logo_asset_id,
        brand_primary_color=brand_primary_color,
        brand_secondary_color=brand_secondary_color,
        hero_image_asset_id=hero_image_asset_id,
        header_html=header_html,
        introduction_html=introduction_html,
        services_section_html=services_section_html,
        benefits_html=benefits_html,
        scope_html=scope_html,
        exclusions_html=exclusions_html,
        terms_html=terms_html,
        footer_html=footer_html,
        gallery_asset_ids=gallery_asset_ids or [],
        service_categories=service_categories or [],
        package_tiers=package_tiers or [],
        is_default=is_default,
        is_active=is_active,
        display_order=kwargs.get("display_order", 0),
        metadata=kwargs.get("metadata", {}),
    )

    db.proposal_templates[template_id] = template
    return template


def get_template(db: InMemoryDB, template_id: int) -> Optional[ProposalTemplate]:
    """Get a template by ID."""
    return db.proposal_templates.get(template_id)


def list_templates(
    db: InMemoryDB,
    is_active: Optional[bool] = None,
    service_category: Optional[str] = None,
    package_tier: Optional[str] = None,
) -> List[ProposalTemplate]:
    """List proposal templates with optional filters."""
    templates = list(db.proposal_templates.values())

    if is_active is not None:
        templates = [t for t in templates if t.is_active == is_active]

    if service_category:
        templates = [
            t for t in templates
            if not t.service_categories or service_category in t.service_categories
        ]

    if package_tier:
        templates = [
            t for t in templates
            if not t.package_tiers or package_tier in t.package_tiers
        ]

    # Sort by display order, then by name
    templates.sort(key=lambda t: (t.display_order, t.name))
    return templates


def update_template(
    db: InMemoryDB,
    template_id: int,
    **updates
) -> Optional[ProposalTemplate]:
    """Update a proposal template."""
    template = db.proposal_templates.get(template_id)
    if not template:
        return None

    # Update allowed fields
    for key, value in updates.items():
        if hasattr(template, key) and key not in ["id", "created_at"]:
            setattr(template, key, value)

    template.updated_at = datetime.utcnow()
    return template


def delete_template(db: InMemoryDB, template_id: int) -> bool:
    """Delete a proposal template."""
    if template_id in db.proposal_templates:
        del db.proposal_templates[template_id]
        return True
    return False


def get_default_template(db: InMemoryDB) -> Optional[ProposalTemplate]:
    """Get the default proposal template."""
    for template in db.proposal_templates.values():
        if template.is_default and template.is_active:
            return template
    return None


# Asset Management Functions

def create_asset(
    db: InMemoryDB,
    name: str,
    filename: str,
    file_path: str,
    file_type: str,
    file_size: int,
    url: str,
    category: str = "general",
    tags: Optional[List[str]] = None,
    **kwargs
) -> Asset:
    """Create a new asset."""

    asset_id = get_next_asset_id()

    asset = Asset(
        id=asset_id,
        name=name,
        filename=filename,
        file_path=file_path,
        file_type=file_type,
        file_size=file_size,
        url=url,
        category=category,
        tags=tags or [],
        metadata=kwargs.get("metadata", {}),
    )

    db.assets[asset_id] = asset
    return asset


def get_asset(db: InMemoryDB, asset_id: int) -> Optional[Asset]:
    """Get an asset by ID."""
    return db.assets.get(asset_id)


def list_assets(
    db: InMemoryDB,
    category: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> List[Asset]:
    """List assets with optional filters."""
    assets = list(db.assets.values())

    if category:
        assets = [a for a in assets if a.category == category]

    if tags:
        assets = [
            a for a in assets
            if any(tag in a.tags for tag in tags)
        ]

    # Sort by created_at descending (newest first)
    assets.sort(key=lambda a: a.created_at, reverse=True)
    return assets


def delete_asset(db: InMemoryDB, asset_id: int) -> bool:
    """Delete an asset."""
    if asset_id in db.assets:
        # Get the asset to get file path
        asset = db.assets[asset_id]

        # Delete the physical file if it exists
        if os.path.exists(asset.file_path):
            try:
                os.remove(asset.file_path)
            except Exception:
                pass  # Continue even if file deletion fails

        del db.assets[asset_id]
        return True
    return False


# Proposal Generation Functions

def render_proposal(
    db: InMemoryDB,
    quote: Quote,
    template: Optional[ProposalTemplate] = None,
) -> str:
    """Render a proposal HTML for a quote using a template.

    Replaces tokenized variables with actual data.
    """
    # Get template (use default if not specified)
    if not template:
        template = get_default_template(db)
        if not template:
            # Create a basic template if none exists
            template = _get_fallback_template()

    # Get related data
    from app.services.quote_service import get_quote_with_items
    from app.db import db as global_db

    quote_with_items = get_quote_with_items(global_db, quote.id)
    if not quote_with_items:
        return "<html><body>Quote not found</body></html>"

    # Get contact/lead data
    contact = global_db.contacts.get(quote.contact_id)
    lead = global_db.leads.get(quote.lead_id)

    # Build token replacement dictionary
    tokens = {
        # Customer tokens
        "{{customer.first_name}}": contact.first_name or "" if contact else "",
        "{{customer.last_name}}": contact.last_name or "" if contact else "",
        "{{customer.full_name}}": contact.full_name if contact else "",
        "{{customer.email}}": contact.email or "" if contact else "",
        "{{customer.phone}}": contact.phone or "" if contact else "",
        "{{customer.address}}": contact.custom_fields.get("address", "") if contact else "",

        # Quote tokens
        "{{quote.number}}": quote.quote_number,
        "{{quote.title}}": quote.title,
        "{{quote.total}}": f"${quote.total:,.2f}",
        "{{quote.subtotal}}": f"${quote.subtotal:,.2f}",
        "{{quote.tax_amount}}": f"${quote.tax_amount:,.2f}",
        "{{quote.discount_amount}}": f"${quote.discount_amount:,.2f}",
        "{{quote.valid_until}}": quote.valid_until.strftime("%B %d, %Y") if quote.valid_until else "N/A",
        "{{quote.created_at}}": quote.created_at.strftime("%B %d, %Y"),

        # Service tokens
        "{{service.names}}": ", ".join([item.service_name for item in quote_with_items.get("items", [])]),
        "{{service.details}}": _render_service_details(quote_with_items.get("items", [])),

        # Package tokens (if applicable)
        "{{package.name}}": quote.metadata.get("package_name", ""),
        "{{job.date_window}}": quote.metadata.get("job_date_window", "TBD"),
    }

    # Combine all HTML sections
    html_sections = [
        template.header_html,
        template.introduction_html,
        template.services_section_html,
        template.benefits_html,
        template.scope_html,
        template.exclusions_html,
        template.terms_html,
        template.footer_html,
    ]

    combined_html = "\n".join(html_sections)

    # Replace all tokens
    for token, value in tokens.items():
        combined_html = combined_html.replace(token, str(value))

    # Get asset URLs for hero and logo
    logo_url = ""
    hero_url = ""

    if template.brand_logo_asset_id:
        logo_asset = get_asset(db, template.brand_logo_asset_id)
        if logo_asset:
            logo_url = logo_asset.url

    if template.hero_image_asset_id:
        hero_asset = get_asset(db, template.hero_image_asset_id)
        if hero_asset:
            hero_url = hero_asset.url

    # Build gallery HTML
    gallery_html = ""
    if template.gallery_asset_ids:
        gallery_items = []
        for asset_id in template.gallery_asset_ids:
            asset = get_asset(db, asset_id)
            if asset:
                gallery_items.append(f'<img src="{asset.url}" alt="{asset.name}" class="gallery-image">')
        if gallery_items:
            gallery_html = f'<div class="gallery">{"".join(gallery_items)}</div>'

    # Wrap in full HTML document with branding
    full_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{quote.title} - Proposal {quote.quote_number}</title>
    <style>
        :root {{
            --primary-color: {template.brand_primary_color};
            --secondary-color: {template.brand_secondary_color};
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            background: var(--primary-color);
            color: white;
            padding: 2rem;
            text-align: center;
        }}
        .header img {{
            max-width: 200px;
            height: auto;
            margin-bottom: 1rem;
        }}
        .hero {{
            width: 100%;
            height: 400px;
            object-fit: cover;
        }}
        .content {{
            padding: 2rem;
        }}
        .section {{
            margin-bottom: 2rem;
        }}
        .section h2 {{
            color: var(--primary-color);
            border-bottom: 2px solid var(--primary-color);
            padding-bottom: 0.5rem;
        }}
        .service-item {{
            padding: 1rem;
            margin: 1rem 0;
            background: #f9f9f9;
            border-left: 4px solid var(--primary-color);
        }}
        .price-box {{
            background: var(--primary-color);
            color: white;
            padding: 2rem;
            text-align: center;
            font-size: 1.5rem;
            margin: 2rem 0;
        }}
        .cta-button {{
            display: inline-block;
            background: var(--secondary-color);
            color: white;
            padding: 1rem 2rem;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            margin: 1rem 0;
        }}
        .cta-button:hover {{
            opacity: 0.9;
        }}
        .gallery {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }}
        .gallery-image {{
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-radius: 5px;
        }}
        .footer {{
            background: #f5f5f5;
            padding: 2rem;
            text-align: center;
            color: #666;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            {f'<img src="{logo_url}" alt="Company Logo">' if logo_url else ''}
            <h1>Proposal {quote.quote_number}</h1>
            <p>{quote.title}</p>
        </div>

        {f'<img src="{hero_url}" alt="Hero Image" class="hero">' if hero_url else ''}

        <div class="content">
            {combined_html}

            {gallery_html}

            <div class="price-box">
                <div>Total Investment</div>
                <div style="font-size: 2.5rem; font-weight: bold;">${quote.total:,.2f}</div>
            </div>

            {_render_acceptance_section(quote, template)}
        </div>

        <div class="footer">
            <p>Proposal generated on {datetime.utcnow().strftime("%B %d, %Y")}</p>
            <p>Thank you for considering our services!</p>
        </div>
    </div>
</body>
</html>
"""

    return full_html


def _render_acceptance_section(quote, template):
    """Render the acceptance section based on quote status."""

    # If already accepted, show acceptance confirmation
    if quote.status == "ACCEPTED":
        return f"""
        <div style="background: #d4edda; border: 2px solid #28a745; padding: 2rem; margin: 2rem 0; border-radius: 10px; text-align: center;">
            <div style="font-size: 3rem; color: #28a745; margin-bottom: 1rem;">✓</div>
            <h2 style="color: #28a745; margin: 0;">Proposal Accepted!</h2>
            <p style="margin-top: 1rem; color: #155724;">
                Thank you for accepting this proposal on {quote.accepted_at.strftime("%B %d, %Y at %I:%M %p") if quote.accepted_at else "N/A"}.<br>
                Signed by: <strong>{quote.signature_name or "N/A"}</strong>
            </p>
            <div style="margin-top: 2rem;">
                <a href="/api/v1/sales/proposals/{quote.id}/pdf" class="cta-button" style="background: #28a745;">
                    Download Accepted Proposal
                </a>
            </div>
        </div>
        """

    # If not yet accepted, show acceptance form
    if quote.status in ["SENT", "VIEWED"]:
        # Build initialed clauses HTML if template has them
        clauses_html = ""
        if template and template.initialed_clauses:
            clauses_items = []
            for clause in template.initialed_clauses:
                required_text = " *" if clause.get("required", False) else ""
                clauses_items.append(f'''
                <div class="clause-item">
                    <h4>{clause.get("title", "Clause")}{required_text}</h4>
                    <p>{clause.get("text", "")}</p>
                    <div style="margin-top: 0.5rem;">
                        <label for="clause_{clause.get('id')}">Your Initials:</label>
                        <input type="text" id="clause_{clause.get('id')}" name="clause_{clause.get('id')}" maxlength="5" required="{str(clause.get('required', False)).lower()}" style="width: 80px; margin-left: 0.5rem; padding: 0.3rem;">
                    </div>
                </div>
                ''')
            if clauses_items:
                clauses_html = f'''
                <div style="margin: 2rem 0; padding: 1.5rem; background: #fff3cd; border: 1px solid #ffc107; border-radius: 5px;">
                    <h3 style="margin-top: 0; color: #856404;">Important Clauses Requiring Initials</h3>
                    <p style="color: #856404; font-size: 0.9rem;">Please read and initial each clause below:</p>
                    {"".join(clauses_items)}
                </div>
                '''

        return f'''
        <div id="acceptance-form" style="margin: 2rem 0; padding: 2rem; background: #f8f9fa; border: 2px solid #007bff; border-radius: 10px;">
            <h2 style="text-align: center; color: #007bff; margin-top: 0;">Accept This Proposal</h2>
            <p style="text-align: center; color: #666;">Please review and sign below to accept this proposal</p>

            {clauses_html}

            <form id="accept-form" onsubmit="handleAcceptance(event)">
                <div style="margin: 1.5rem 0;">
                    <label for="signature_name" style="display: block; font-weight: bold; margin-bottom: 0.5rem;">
                        Full Name (Signature) *
                    </label>
                    <input type="text" id="signature_name" name="signature_name" required style="width: 100%; padding: 0.75rem; font-size: 1rem; border: 1px solid #ccc; border-radius: 5px;" placeholder="Type your full name">
                </div>

                <div style="margin: 1.5rem 0;">
                    <label style="display: flex; align-items: flex-start; cursor: pointer;">
                        <input type="checkbox" id="terms_accepted" name="terms_accepted" required style="margin-top: 0.3rem; margin-right: 0.75rem;">
                        <span>I have read and agree to the terms and conditions outlined in this proposal. By signing, I authorize the work to begin as described. *</span>
                    </label>
                </div>

                <div id="error-message" style="display: none; padding: 1rem; background: #f8d7da; border: 1px solid #f5c2c7; color: #842029; border-radius: 5px; margin: 1rem 0;"></div>
                <div id="success-message" style="display: none; padding: 1rem; background: #d1e7dd; border: 1px solid #badbcc; color: #0f5132; border-radius: 5px; margin: 1rem 0;"></div>

                <div style="text-align: center; margin-top: 2rem;">
                    <button type="submit" id="submit-btn" class="cta-button" style="font-size: 1.1rem; padding: 1rem 3rem;">
                        Accept & Sign Proposal
                    </button>
                </div>

                <p style="text-align: center; color: #999; font-size: 0.85rem; margin-top: 1rem;">
                    * Required fields
                </p>
            </form>
        </div>

        <script>
        async function handleAcceptance(e) {{
            e.preventDefault();

            const submitBtn = document.getElementById('submit-btn');
            const errorDiv = document.getElementById('error-message');
            const successDiv = document.getElementById('success-message');

            // Disable submit button
            submitBtn.disabled = true;
            submitBtn.textContent = 'Processing...';
            errorDiv.style.display = 'none';
            successDiv.style.display = 'none';

            // Gather form data
            const signature_name = document.getElementById('signature_name').value.trim();
            const terms_accepted = document.getElementById('terms_accepted').checked;

            // Gather initialed clauses
            const initialed_clauses = {{}};
            const clauseInputs = document.querySelectorAll('[id^="clause_"]');
            clauseInputs.forEach(input => {{
                const clauseId = input.id.replace('clause_', '');
                const initials = input.value.trim();
                if (initials) {{
                    initialed_clauses[clauseId] = initials;
                }}
            }});

            // Validate
            if (!signature_name) {{
                errorDiv.textContent = 'Please enter your full name';
                errorDiv.style.display = 'block';
                submitBtn.disabled = false;
                submitBtn.textContent = 'Accept & Sign Proposal';
                return;
            }}

            if (!terms_accepted) {{
                errorDiv.textContent = 'You must accept the terms and conditions';
                errorDiv.style.display = 'block';
                submitBtn.disabled = false;
                submitBtn.textContent = 'Accept & Sign Proposal';
                return;
            }}

            try {{
                const response = await fetch('/api/v1/sales/proposals/{quote.id}/accept', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{
                        signature_name,
                        terms_accepted,
                        initialed_clauses
                    }})
                }});

                const data = await response.json();

                if (!response.ok) {{
                    throw new Error(data.detail || 'Failed to accept proposal');
                }}

                // Success!
                successDiv.textContent = data.message || 'Proposal accepted successfully!';
                successDiv.style.display = 'block';

                // Reload page after 2 seconds to show acceptance confirmation
                setTimeout(() => {{
                    window.location.reload();
                }}, 2000);

            }} catch (error) {{
                errorDiv.textContent = error.message || 'Failed to accept proposal. Please try again.';
                errorDiv.style.display = 'block';
                submitBtn.disabled = false;
                submitBtn.textContent = 'Accept & Sign Proposal';
            }}
        }}
        </script>
        '''

    # For other statuses, show nothing or a message
    return f'''
    <div style="text-align: center; padding: 2rem; color: #666;">
        <p>This proposal is currently in <strong>{quote.status}</strong> status.</p>
    </div>
    '''


def _render_service_details(items: List[Any]) -> str:
    """Render service line items as HTML."""
    if not items:
        return "<p>No services specified</p>"

    html = "<div class='service-items'>"
    for item in items:
        html += f"""
        <div class="service-item">
            <h3>{item.service_name}</h3>
            <p>{item.description}</p>
            <div style="display: flex; justify-content: space-between;">
                <span>Quantity: {item.quantity} @ ${item.unit_price:,.2f}</span>
                <strong>${item.total:,.2f}</strong>
            </div>
        </div>
        """
    html += "</div>"
    return html


def _get_fallback_template() -> ProposalTemplate:
    """Get a basic fallback template if none exists."""
    return ProposalTemplate(
        id=0,
        name="Default Template",
        description="Basic fallback template",
        header_html="<h1>{{quote.title}}</h1>",
        introduction_html="<p>Dear {{customer.full_name}},</p><p>Thank you for considering our services. Here is your custom proposal.</p>",
        services_section_html="<h2>Services Included</h2>{{service.details}}",
        benefits_html="<h2>Why Choose Us</h2><ul><li>Quality workmanship</li><li>Professional service</li><li>Satisfaction guaranteed</li></ul>",
        scope_html="<h2>Scope of Work</h2><p>We will complete all services listed above to the highest standard.</p>",
        exclusions_html="<h2>Exclusions</h2><p>Additional services not listed above may incur extra charges.</p>",
        terms_html="<h2>Terms & Conditions</h2><p>Payment is due upon completion. Valid until {{quote.valid_until}}.</p>",
        footer_html="<p>If you have any questions, please don't hesitate to contact us.</p>",
    )
