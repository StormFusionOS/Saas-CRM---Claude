"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
CRM API Data Models (In-Memory).

Simple dataclass models for in-memory operations.
For SQLAlchemy models used in schema tooling, see db_models.py
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class LeadStatus(str, Enum):
    """Lead pipeline status."""

    NEW = "NEW"
    CONTACTED = "CONTACTED"
    QUOTED = "QUOTED"
    SCHEDULED = "SCHEDULED"
    WON = "WON"
    LOST = "LOST"


class InteractionType(str, Enum):
    """Type of customer interaction."""

    EMAIL = "EMAIL"
    SMS = "SMS"
    PHONE = "PHONE"
    MEETING = "MEETING"
    NOTE = "NOTE"
    WEBHOOK = "WEBHOOK"


class LeadSource(str, Enum):
    """Source of lead."""

    FACEBOOK = "FACEBOOK"
    GOOGLE = "GOOGLE"
    TWILIO = "TWILIO"
    MANUAL = "MANUAL"
    IMPORT = "IMPORT"
    API = "API"


class QuoteStatus(str, Enum):
    """Quote status lifecycle."""

    DRAFT = "DRAFT"
    PENDING = "PENDING"
    SENT = "SENT"
    VIEWED = "VIEWED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


@dataclass
class User:
    """CRM user model."""

    id: int
    email: str
    hashed_password: str
    full_name: str
    roles: List[str]
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


@dataclass
class Contact:
    """Contact/customer model."""

    id: int
    email: Optional[str] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    custom_fields: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    last_contacted_at: Optional[datetime] = None

    @property
    def full_name(self) -> str:
        """Get full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or "Unknown"


@dataclass
class Lead:
    """Sales lead model."""

    id: int
    contact_id: int
    status: str = LeadStatus.NEW.value
    source: str = LeadSource.MANUAL.value
    value: Optional[float] = None
    assigned_to_id: Optional[int] = None
    probability: int = 0  # 0-100
    expected_close_date: Optional[datetime] = None
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    won_at: Optional[datetime] = None
    lost_at: Optional[datetime] = None


@dataclass
class Interaction:
    """Customer interaction record."""

    id: int
    contact_id: int
    lead_id: Optional[int] = None
    user_id: Optional[int] = None
    interaction_type: str = InteractionType.NOTE.value
    direction: str = "INBOUND"  # INBOUND, OUTBOUND
    subject: Optional[str] = None
    body: str = ""
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AutoReplyRule:
    """Auto-reply rule configuration."""

    id: int
    name: str
    trigger_source: str  # FACEBOOK, GOOGLE, TWILIO, etc.
    trigger_conditions: dict = field(default_factory=dict)
    reply_template: str = ""
    reply_channel: str = "EMAIL"  # EMAIL, SMS
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


@dataclass
class PricebookItem:
    """Pricebook service item."""

    id: int
    name: str
    description: str
    unit: str  # e.g., "sq_ft", "linear_ft", "each"
    base_price: float
    formula: str  # e.g., "base_price * sq_ft", "base_price + (stories * 50)"
    category: str = "general"  # house_wash, roof_wash, etc.
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Estimate:
    """Estimate/Quote for a lead."""

    id: int
    lead_id: int
    contact_id: int
    service_ids: List[int]
    inputs: dict  # e.g., {"sq_ft": 2500, "stories": 2}
    good_tier: dict  # {"price": 299, "items": [...]}
    better_tier: dict  # {"price": 399, "items": [...]}
    best_tier: dict  # {"price": 499, "items": [...]}
    selected_tier: Optional[str] = None  # "good", "better", "best"
    deposit_amount: Optional[float] = None
    deposit_due: Optional[datetime] = None
    status: str = "draft"  # draft, sent, accepted, rejected
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None


@dataclass
class Job:
    """Job created from accepted estimate."""

    id: int
    lead_id: int
    estimate_id: int
    contact_id: int
    title: str
    total_price: float
    deposit_amount: float
    deposit_paid: bool = False
    status: str = "pending"  # pending, scheduled, in_progress, completed, cancelled
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


@dataclass
class Service:
    """Service offering for quotes.

    Represents a service that can be added to quotes.
    More focused than PricebookItem - designed for the quoting engine.
    """

    id: int
    name: str
    description: str
    category: str  # e.g., "house_wash", "roof_wash", "window_cleaning"
    base_price: float
    unit: str  # e.g., "sq_ft", "linear_ft", "each", "hour"
    min_price: Optional[float] = None  # Minimum price floor for this service
    pricing_formula: Optional[str] = None  # e.g., "base_price * sq_ft + (stories * 50)"
    modifiers: dict = field(default_factory=dict)  # Optional pricing modifiers (e.g., {"difficulty": 1.2})
    is_active: bool = True
    display_order: int = 0
    metadata: dict = field(default_factory=dict)  # Additional service-specific data
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


@dataclass
class QuoteItem:
    """Line item in a quote.

    Represents a single service line item within a quote.
    """

    id: int
    quote_id: int
    service_id: int
    service_name: str  # Snapshot of service name at time of quote
    description: str
    quantity: float = 1.0
    unit_price: float = 0.0
    subtotal: float = 0.0  # quantity * unit_price
    discount_percent: float = 0.0
    discount_amount: float = 0.0
    tax_percent: float = 0.0
    tax_amount: float = 0.0
    total: float = 0.0  # subtotal - discount_amount + tax_amount
    display_order: int = 0
    metadata: dict = field(default_factory=dict)  # e.g., {"sq_ft": 2500, "stories": 2}
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Quote:
    """Formal quote/proposal for a lead.

    Main quoting engine model. Represents a formal quote with line items,
    pricing, terms, and lifecycle tracking.
    """

    id: int
    lead_id: int
    contact_id: int
    quote_number: str  # e.g., "Q-2025-0001"
    title: str
    status: str = QuoteStatus.DRAFT.value
    subtotal: float = 0.0
    discount_amount: float = 0.0
    tax_amount: float = 0.0
    total: float = 0.0
    valid_until: Optional[datetime] = None
    terms: str = ""  # Payment terms, service terms, etc.
    notes: str = ""  # Internal notes
    public_notes: str = ""  # Notes visible to customer
    proposal_template_id: Optional[int] = None  # Template to use for customer-facing proposal
    proposal_url: Optional[str] = None  # Public URL for customer to view proposal

    # E-signature fields
    signature_name: Optional[str] = None  # Name typed for signature
    signature_ip: Optional[str] = None  # IP address of signer
    signature_user_agent: Optional[str] = None  # Browser user agent of signer
    terms_accepted: bool = False  # Whether T&Cs were accepted
    initialed_clauses: dict = field(default_factory=dict)  # {clause_id: initials}

    created_by_id: Optional[int] = None
    approved_by_id: Optional[int] = None
    sent_at: Optional[datetime] = None
    viewed_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    expired_at: Optional[datetime] = None
    metadata: dict = field(default_factory=dict)  # Flexible field for extensions
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


@dataclass
class Asset:
    """Asset storage for proposal templates.

    Stores images, logos, and other files used in proposal templates.
    """

    id: int
    name: str  # Display name
    filename: str  # Original filename
    file_path: str  # Relative path in assets directory
    file_type: str  # e.g., "image/png", "image/jpeg", "application/pdf"
    file_size: int  # Size in bytes
    url: str  # Public URL to access the asset
    category: str = "general"  # e.g., "logo", "hero", "gallery", "general"
    tags: List[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


@dataclass
class ProposalTemplate:
    """Proposal template for customer-facing quotes.

    Defines the layout, branding, and content structure for proposals
    that customers see when they receive a quote.
    """

    id: int
    name: str  # Internal name for the template
    description: str = ""

    # Brand settings
    brand_logo_asset_id: Optional[int] = None
    brand_primary_color: str = "#0066cc"  # Hex color
    brand_secondary_color: str = "#003366"
    hero_image_asset_id: Optional[int] = None

    # Content sections (HTML with tokenized variables)
    header_html: str = ""  # Header section
    introduction_html: str = ""  # Introduction/welcome section
    services_section_html: str = ""  # Services list presentation
    benefits_html: str = ""  # Benefit bullets
    scope_html: str = ""  # Scope of work details
    exclusions_html: str = ""  # What's NOT included
    terms_html: str = ""  # Terms and conditions
    footer_html: str = ""  # Footer section

    # Gallery assets
    gallery_asset_ids: List[int] = field(default_factory=list)

    # Initialed clauses (require customer initials)
    # Format: [{"id": "clause_1", "title": "Ladder Waiver", "text": "I understand...", "required": true}]
    initialed_clauses: List[dict] = field(default_factory=list)

    # Template metadata
    service_categories: List[str] = field(default_factory=list)  # Which services this applies to
    package_tiers: List[str] = field(default_factory=list)  # e.g., ["good", "better", "best"]
    is_default: bool = False  # Use as default if no specific template selected
    is_active: bool = True
    display_order: int = 0

    # Available tokens for this template
    available_tokens: List[str] = field(default_factory=lambda: [
        "{{customer.first_name}}",
        "{{customer.last_name}}",
        "{{customer.full_name}}",
        "{{customer.email}}",
        "{{customer.phone}}",
        "{{customer.address}}",
        "{{quote.number}}",
        "{{quote.title}}",
        "{{quote.total}}",
        "{{quote.subtotal}}",
        "{{quote.tax_amount}}",
        "{{quote.discount_amount}}",
        "{{quote.valid_until}}",
        "{{quote.created_at}}",
        "{{service.names}}",
        "{{service.details}}",
        "{{package.name}}",
        "{{job.date_window}}",
    ])

    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


@dataclass
class AvailabilityConfig:
    """Availability configuration for scheduling.

    Defines business hours, buffer times, and scheduling rules.
    """

    id: int
    name: str = "Default Availability"

    # Business hours (simplified - same for all days)
    start_time: str = "09:00"  # HH:MM format
    end_time: str = "17:00"    # HH:MM format
    working_days: List[int] = field(default_factory=lambda: [1, 2, 3, 4, 5])  # Monday=1, Sunday=7

    # Scheduling rules
    slot_duration_minutes: int = 120  # Default 2-hour slots
    buffer_minutes: int = 30  # Buffer between appointments
    max_appointments_per_day: int = 4
    min_notice_hours: int = 24  # Minimum hours before appointment
    max_days_advance: int = 60  # How far in advance customers can book

    # Blackout dates (dates when no appointments available)
    blackout_dates: List[str] = field(default_factory=list)  # ["2025-12-25", "2025-01-01"]

    is_active: bool = True
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


@dataclass
class Appointment:
    """Customer appointment/booking.

    Represents a scheduled appointment for an accepted quote.
    """

    id: int
    quote_id: int
    contact_id: int
    lead_id: Optional[int] = None

    # Appointment details
    scheduled_start: datetime = field(default_factory=datetime.utcnow)
    scheduled_end: datetime = field(default_factory=datetime.utcnow)
    duration_minutes: int = 120

    # Status tracking
    status: str = "scheduled"  # scheduled, confirmed, in_progress, completed, cancelled, no_show
    confirmed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: str = ""

    # Customer info (snapshot)
    customer_name: str = ""
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None

    # Appointment details
    service_description: str = ""  # What services will be performed
    special_instructions: str = ""  # Customer notes/instructions
    address: str = ""  # Where the service will be performed

    # Notifications
    reminder_sent_at: Optional[datetime] = None
    confirmation_sent_at: Optional[datetime] = None

    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


# ============================================================================
# SmartForm Builder Models
# ============================================================================


@dataclass
class FormField:
    """Form field definition.

    Defines a single field in a form template with validation rules and conditional logic.
    """

    id: str  # Unique field ID (e.g., "customer_name", "service_type")
    label: str  # Display label
    field_type: str  # text, email, phone, number, select, multiselect, checkbox, radio, textarea, date, file

    # Validation
    required: bool = False
    placeholder: str = ""
    help_text: str = ""

    # Field-specific options
    options: List[str] = field(default_factory=list)  # For select, multiselect, radio
    min_value: Optional[float] = None  # For number fields
    max_value: Optional[float] = None
    min_length: Optional[int] = None  # For text fields
    max_length: Optional[int] = None
    pattern: Optional[str] = None  # Regex validation

    # Conditional logic
    show_if: Optional[Dict[str, Any]] = None  # {"field_id": "expected_value"} or more complex rules

    # Display
    order: int = 0  # Display order
    width: str = "full"  # full, half, third, quarter

    metadata: dict = field(default_factory=dict)


@dataclass
class FormTemplate:
    """Form template definition.

    A reusable form template for collecting customer information.
    """

    id: int
    name: str  # Internal name
    title: str  # Display title for customers
    description: str = ""

    # Fields
    fields: List[FormField] = field(default_factory=list)

    # Settings
    is_active: bool = True
    allow_multiple_submissions: bool = False  # Can same customer submit multiple times?
    require_authentication: bool = False  # Must customer be logged in?

    # Notifications
    send_confirmation_email: bool = True
    confirmation_email_template: str = ""
    notify_staff_on_submission: bool = True
    notification_emails: List[str] = field(default_factory=list)

    # Integration
    attach_to_proposal: bool = False  # Can be attached to proposals?
    attach_to_quote: bool = False  # Can be attached to quotes?

    # Categories/Tags
    category: str = ""  # e.g., "intake", "feedback", "service_request"
    tags: List[str] = field(default_factory=list)

    # Success behavior
    success_message: str = "Thank you for your submission!"
    redirect_url: Optional[str] = None

    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None  # User ID


@dataclass
class FormSubmission:
    """Customer form submission.

    Stores customer responses to a form template.
    """

    id: int
    form_template_id: int

    # Submitted data
    responses: Dict[str, Any] = field(default_factory=dict)  # {"field_id": "value"}

    # Context
    contact_id: Optional[int] = None  # If customer is known
    lead_id: Optional[int] = None
    quote_id: Optional[int] = None  # If submitted via quote
    proposal_id: Optional[int] = None  # If submitted via proposal

    # Submitter info (captured at time of submission)
    submitter_name: str = ""
    submitter_email: Optional[str] = None
    submitter_phone: Optional[str] = None

    # Submission details
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None

    # Status
    status: str = "submitted"  # submitted, reviewed, processed, archived
    reviewed_by: Optional[int] = None  # User ID who reviewed
    reviewed_at: Optional[datetime] = None
    notes: str = ""  # Staff notes about this submission

    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


# ============================================================================
# Follow-Up Automation Models
# ============================================================================


@dataclass
class FollowUpStep:
    """A single step in a follow-up sequence.

    Defines what action to take and when.
    """

    id: str  # Unique step ID within sequence (e.g., "step_1", "day_3_email")
    order: int  # Execution order

    # Timing
    delay_hours: int = 24  # Hours after previous step (or sequence start for first step)

    # Action type
    action_type: str = "email"  # email, sms, task, call

    # Action details
    subject: str = ""  # For emails
    body_template: str = ""  # Template with variables like {{first_name}}
    task_title: str = ""  # For tasks
    task_description: str = ""  # For tasks
    assign_to_role: Optional[str] = None  # Role to assign task to (e.g., "SALES")

    # Conditions (when to execute this step)
    conditions: Dict[str, Any] = field(default_factory=dict)  # e.g., {"lead_status": "NEW"}
    skip_if_responded: bool = True  # Skip if lead already responded

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FollowUpSequence:
    """Follow-up automation sequence template.

    Defines a series of automated follow-up actions.
    """

    id: int
    name: str  # e.g., "New Lead Nurture", "Quote Follow-Up"
    description: str = ""

    # Steps in the sequence
    steps: List[FollowUpStep] = field(default_factory=list)

    # Trigger conditions
    trigger_event: str = "lead_created"  # lead_created, quote_sent, proposal_viewed, form_submitted
    trigger_conditions: Dict[str, Any] = field(default_factory=dict)  # Additional conditions

    # Settings
    is_active: bool = True
    priority: int = 0  # Higher priority sequences execute first

    # Stop conditions
    stop_on_response: bool = True  # Stop if lead responds
    stop_on_status_change: bool = False  # Stop if lead status changes
    stop_statuses: List[str] = field(default_factory=list)  # Statuses that stop the sequence

    # Categorization
    category: str = ""  # nurture, follow_up, reminder, etc.
    tags: List[str] = field(default_factory=list)

    # Statistics
    total_started: int = 0  # How many times this sequence has been started
    total_completed: int = 0  # How many times completed
    total_stopped: int = 0  # How many times stopped early

    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None  # User ID


@dataclass
class FollowUpInstance:
    """Active instance of a follow-up sequence for a specific lead/contact.

    Tracks progress through a sequence.
    """

    id: int
    sequence_id: int  # Which sequence this is running

    # Target
    lead_id: Optional[int] = None
    contact_id: Optional[int] = None
    quote_id: Optional[int] = None  # If triggered by quote

    # Progress
    status: str = "active"  # active, completed, stopped, paused
    current_step_index: int = 0  # Which step we're on
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    stop_reason: str = ""  # Why it was stopped (if applicable)

    # Tracking
    steps_completed: List[str] = field(default_factory=list)  # List of step IDs completed
    last_action_at: Optional[datetime] = None

    # Response tracking
    has_responded: bool = False  # Has the lead responded?
    response_date: Optional[datetime] = None
    response_type: str = ""  # email, call, meeting_booked, etc.

    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


@dataclass
class FollowUpTask:
    """Scheduled task from a follow-up sequence.

    Individual tasks created by automation.
    """

    id: int
    instance_id: int  # Which instance created this task
    sequence_id: int  # Which sequence it's from
    step_id: str  # Which step in the sequence

    # Target
    lead_id: Optional[int] = None
    contact_id: Optional[int] = None

    # Task details
    task_type: str = "email"  # email, sms, call, task
    status: str = "pending"  # pending, sent, completed, failed, skipped

    # Scheduling
    scheduled_for: datetime = field(default_factory=datetime.utcnow)
    executed_at: Optional[datetime] = None

    # Task content
    subject: str = ""
    body: str = ""  # Rendered template
    task_title: str = ""
    task_description: str = ""

    # Assignment (for manual tasks)
    assigned_to: Optional[int] = None  # User ID
    completed_by: Optional[int] = None  # User ID who completed it

    # Results
    success: bool = False
    error_message: str = ""
    response_received: bool = False  # Did we get a response?

    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


# ============================================================================
# Packages & Bundles
# ============================================================================


@dataclass
class PackageItem:
    """A service/item included in a package."""

    pricebook_item_id: int
    quantity: float = 1.0
    unit_override: Optional[str] = None  # Override default unit
    description_override: Optional[str] = None  # Override default description
    price_override: Optional[float] = None  # Override price for this package
    is_optional: bool = False  # Can be removed from package
    display_order: int = 0


@dataclass
class Package:
    """Service package/bundle template.

    Bundles multiple services together at a discounted rate.
    """

    id: int
    name: str
    description: str = ""
    category: str = ""  # e.g., "seasonal", "maintenance", "cleanup"

    # Items in package
    items: List[PackageItem] = field(default_factory=list)

    # Pricing
    pricing_type: str = "fixed"  # fixed, calculated
    fixed_price: Optional[float] = None  # For fixed pricing
    discount_percent: float = 0.0  # For calculated pricing (% off sum of items)

    # Availability
    is_active: bool = True
    valid_from: Optional[datetime] = None  # Seasonal availability
    valid_to: Optional[datetime] = None

    # Display
    image_url: str = ""
    display_order: int = 0
    featured: bool = False  # Show prominently
    tags: List[str] = field(default_factory=list)

    # Terms
    terms: str = ""  # Special terms for this package
    requires_site_visit: bool = False

    # Stats
    times_sold: int = 0
    total_revenue: float = 0.0

    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None


# ============================================================================
# Calendar Connections
# ============================================================================


@dataclass
class CalendarConnection:
    """External calendar connection (Google, Outlook, etc.).

    Stores OAuth credentials and sync settings.
    """

    id: int
    user_id: int  # Which staff member owns this connection
    provider: str = "google"  # google, outlook, apple, etc.
    calendar_id: str = ""  # External calendar ID
    calendar_name: str = ""

    # OAuth/Auth
    access_token: str = ""  # Encrypted in production
    refresh_token: str = ""  # Encrypted in production
    token_expires_at: Optional[datetime] = None

    # Sync settings
    is_active: bool = True
    sync_enabled: bool = True
    sync_direction: str = "bidirectional"  # push, pull, bidirectional
    auto_sync: bool = True
    sync_interval_minutes: int = 15

    # Last sync info
    last_sync_at: Optional[datetime] = None
    last_sync_status: str = ""  # success, error, partial
    last_sync_error: str = ""

    # Stats
    events_synced: int = 0
    sync_failures: int = 0

    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


@dataclass
class CalendarEvent:
    """Calendar event sync record.

    Tracks which CRM appointments have been synced to external calendars.
    """

    id: int
    connection_id: int  # Which calendar connection
    appointment_id: int  # CRM appointment ID
    external_event_id: str = ""  # ID in external calendar

    # Event details (cached)
    title: str = ""
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: datetime = field(default_factory=datetime.utcnow)
    location: str = ""
    description: str = ""

    # Sync status
    sync_status: str = "pending"  # pending, synced, error, deleted
    last_synced_at: Optional[datetime] = None
    sync_error: str = ""

    # Attendees
    attendees: List[str] = field(default_factory=list)  # Email addresses

    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


# ============================================================================
# Text Hub / SMS
# ============================================================================


@dataclass
class SMSMessage:
    """Individual SMS message.

    Tracks all SMS communications with contacts/leads.
    """

    id: int
    conversation_id: Optional[int] = None  # Group related messages
    contact_id: Optional[int] = None
    lead_id: Optional[int] = None

    # Phone numbers
    from_number: str = ""  # Sender phone (E.164 format)
    to_number: str = ""    # Recipient phone (E.164 format)

    # Message content
    body: str = ""
    direction: str = "outbound"  # inbound, outbound
    status: str = "pending"  # pending, sent, delivered, failed, received

    # Provider info (Twilio, etc.)
    provider: str = "twilio"
    provider_message_id: str = ""  # External message ID
    provider_status: str = ""

    # Delivery tracking
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    error_message: str = ""

    # Context
    sent_by: Optional[int] = None  # User ID who sent it
    template_id: Optional[int] = None  # If sent from template

    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


@dataclass
class SMSConversation:
    """SMS conversation thread with a contact.

    Groups messages with a contact for easier tracking.
    """

    id: int
    contact_id: Optional[int] = None
    lead_id: Optional[int] = None
    phone_number: str = ""  # Contact's phone number

    # Conversation details
    subject: str = ""  # Optional subject/title
    status: str = "active"  # active, archived, closed

    # Message counts
    message_count: int = 0
    unread_count: int = 0

    # Last activity
    last_message_at: Optional[datetime] = None
    last_message_preview: str = ""
    last_message_direction: str = ""

    # Assignment
    assigned_to: Optional[int] = None  # User ID

    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


@dataclass
class SMSTemplate:
    """Reusable SMS message template.

    Pre-written messages with variable substitution.
    """

    id: int
    name: str
    category: str = ""  # appointment_reminder, follow_up, thank_you, etc.

    # Template content
    body: str = ""  # Can include {{variables}}

    # Usage
    is_active: bool = True
    times_used: int = 0

    # Variables available
    variables: List[str] = field(default_factory=list)  # e.g., ["first_name", "appointment_date"]

    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None


# Auto-incrementing ID counters
_contact_id_counter = 1
_lead_id_counter = 1
_interaction_id_counter = 1
_auto_reply_rule_id_counter = 1
_pricebook_item_id_counter = 1
_estimate_id_counter = 1
_job_id_counter = 1
_service_id_counter = 1
_quote_id_counter = 1
_quote_item_id_counter = 1
_asset_id_counter = 1
_proposal_template_id_counter = 1
_availability_config_id_counter = 1
_appointment_id_counter = 1
_form_template_id_counter = 1
_form_submission_id_counter = 1
_followup_sequence_id_counter = 1
_followup_instance_id_counter = 1
_followup_task_id_counter = 1
_package_id_counter = 1
_calendar_connection_id_counter = 1
_calendar_event_id_counter = 1
_sms_message_id_counter = 1
_sms_conversation_id_counter = 1
_sms_template_id_counter = 1


def get_next_contact_id() -> int:
    """Get next contact ID."""
    global _contact_id_counter
    id = _contact_id_counter
    _contact_id_counter += 1
    return id


def get_next_lead_id() -> int:
    """Get next lead ID."""
    global _lead_id_counter
    id = _lead_id_counter
    _lead_id_counter += 1
    return id


def get_next_interaction_id() -> int:
    """Get next interaction ID."""
    global _interaction_id_counter
    id = _interaction_id_counter
    _interaction_id_counter += 1
    return id


def get_next_auto_reply_rule_id() -> int:
    """Get next auto-reply rule ID."""
    global _auto_reply_rule_id_counter
    id = _auto_reply_rule_id_counter
    _auto_reply_rule_id_counter += 1
    return id


def get_next_pricebook_item_id() -> int:
    """Get next pricebook item ID."""
    global _pricebook_item_id_counter
    id = _pricebook_item_id_counter
    _pricebook_item_id_counter += 1
    return id


def get_next_estimate_id() -> int:
    """Get next estimate ID."""
    global _estimate_id_counter
    id = _estimate_id_counter
    _estimate_id_counter += 1
    return id


def get_next_job_id() -> int:
    """Get next job ID."""
    global _job_id_counter
    id = _job_id_counter
    _job_id_counter += 1
    return id


def get_next_service_id() -> int:
    """Get next service ID."""
    global _service_id_counter
    id = _service_id_counter
    _service_id_counter += 1
    return id


def get_next_quote_id() -> int:
    """Get next quote ID."""
    global _quote_id_counter
    id = _quote_id_counter
    _quote_id_counter += 1
    return id


def get_next_quote_item_id() -> int:
    """Get next quote item ID."""
    global _quote_item_id_counter
    id = _quote_item_id_counter
    _quote_item_id_counter += 1
    return id


def get_next_asset_id() -> int:
    """Get next asset ID."""
    global _asset_id_counter
    id = _asset_id_counter
    _asset_id_counter += 1
    return id


def get_next_proposal_template_id() -> int:
    """Get next proposal template ID."""
    global _proposal_template_id_counter
    id = _proposal_template_id_counter
    _proposal_template_id_counter += 1
    return id


def get_next_availability_config_id() -> int:
    """Get next availability config ID."""
    global _availability_config_id_counter
    id = _availability_config_id_counter
    _availability_config_id_counter += 1
    return id


def get_next_appointment_id() -> int:
    """Get next appointment ID."""
    global _appointment_id_counter
    id = _appointment_id_counter
    _appointment_id_counter += 1
    return id


def get_next_form_template_id() -> int:
    """Get next form template ID."""
    global _form_template_id_counter
    id = _form_template_id_counter
    _form_template_id_counter += 1
    return id


def get_next_form_submission_id() -> int:
    """Get next form submission ID."""
    global _form_submission_id_counter
    id = _form_submission_id_counter
    _form_submission_id_counter += 1
    return id


def get_next_followup_sequence_id() -> int:
    """Get next followup sequence ID."""
    global _followup_sequence_id_counter
    id = _followup_sequence_id_counter
    _followup_sequence_id_counter += 1
    return id


def get_next_followup_instance_id() -> int:
    """Get next followup instance ID."""
    global _followup_instance_id_counter
    id = _followup_instance_id_counter
    _followup_instance_id_counter += 1
    return id


def get_next_followup_task_id() -> int:
    """Get next followup task ID."""
    global _followup_task_id_counter
    id = _followup_task_id_counter
    _followup_task_id_counter += 1
    return id


def get_next_package_id() -> int:
    """Get next package ID."""
    global _package_id_counter
    id = _package_id_counter
    _package_id_counter += 1
    return id


def get_next_calendar_connection_id() -> int:
    """Get next calendar connection ID."""
    global _calendar_connection_id_counter
    id = _calendar_connection_id_counter
    _calendar_connection_id_counter += 1
    return id


def get_next_calendar_event_id() -> int:
    """Get next calendar event ID."""
    global _calendar_event_id_counter
    id = _calendar_event_id_counter
    _calendar_event_id_counter += 1
    return id


def get_next_sms_message_id() -> int:
    """Get next SMS message ID."""
    global _sms_message_id_counter
    id = _sms_message_id_counter
    _sms_message_id_counter += 1
    return id


def get_next_sms_conversation_id() -> int:
    """Get next SMS conversation ID."""
    global _sms_conversation_id_counter
    id = _sms_conversation_id_counter
    _sms_conversation_id_counter += 1
    return id


def get_next_sms_template_id() -> int:
    """Get next SMS template ID."""
    global _sms_template_id_counter
    id = _sms_template_id_counter
    _sms_template_id_counter += 1
    return id


# ============================================================================
# Payments & Deposits
# ============================================================================


@dataclass
class PaymentMethod:
    """Customer payment method (credit card, ACH, etc.)."""

    id: int
    contact_id: int
    lead_id: Optional[int] = None

    # Method type
    method_type: str = "card"  # card, ach, check, cash, other

    # Card details (if applicable, last 4 only for security)
    card_last_four: Optional[str] = None
    card_brand: Optional[str] = None  # visa, mastercard, amex, discover
    card_exp_month: Optional[int] = None
    card_exp_year: Optional[int] = None

    # ACH details (if applicable)
    bank_name: Optional[str] = None
    account_last_four: Optional[str] = None
    account_type: Optional[str] = None  # checking, savings

    # External processor reference
    processor: Optional[str] = None  # stripe, square, authorize_net
    processor_payment_method_id: Optional[str] = None  # External ID

    # Status
    is_default: bool = False
    is_verified: bool = False
    is_active: bool = True

    # Billing address
    billing_name: Optional[str] = None
    billing_address: Optional[str] = None
    billing_city: Optional[str] = None
    billing_state: Optional[str] = None
    billing_zip: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None


@dataclass
class Payment:
    """Payment transaction record."""

    id: int
    contact_id: int
    amount: float  # Required field - must come before optional fields

    # Optional references
    lead_id: Optional[int] = None
    quote_id: Optional[int] = None

    # Payment details
    currency: str = "USD"
    payment_method_id: Optional[int] = None
    payment_type: str = "payment"  # payment, deposit, refund

    # Status
    status: str = "pending"  # pending, processing, succeeded, failed, cancelled, refunded
    failure_reason: Optional[str] = None

    # External processor
    processor: Optional[str] = None  # stripe, square, authorize_net, manual
    processor_transaction_id: Optional[str] = None
    processor_fee: Optional[float] = None

    # Metadata
    description: str = ""
    notes: Optional[str] = None
    receipt_url: Optional[str] = None
    receipt_number: Optional[str] = None

    # Accounting
    applied_to_quote: bool = False
    refund_amount: float = 0.0
    net_amount: Optional[float] = None  # amount - processor_fee - refund_amount

    metadata: Dict[str, Any] = field(default_factory=dict)
    processed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None


@dataclass
class Refund:
    """Refund transaction record."""

    id: int
    payment_id: int
    contact_id: int

    # Refund details
    amount: float
    currency: str = "USD"
    reason: str = ""
    status: str = "pending"  # pending, processing, succeeded, failed

    # External processor
    processor: Optional[str] = None
    processor_refund_id: Optional[str] = None

    # Metadata
    notes: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)
    processed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None


@dataclass
class DepositRequest:
    """Deposit request for quote acceptance."""

    id: int
    quote_id: int
    contact_id: int
    amount: float  # Required field - must come before optional fields

    # Optional references
    lead_id: Optional[int] = None

    # Deposit details
    deposit_type: str = "percentage"  # percentage, fixed
    percentage: Optional[float] = None  # If type is percentage (e.g., 0.50 for 50%)
    due_date: Optional[datetime] = None

    # Status
    status: str = "pending"  # pending, paid, waived, expired
    payment_id: Optional[int] = None  # Link to Payment if paid

    # Notification
    reminder_sent: bool = False
    reminder_count: int = 0
    last_reminder_at: Optional[datetime] = None

    # Metadata
    notes: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None


# ID counters for payments
_payment_method_id_counter = 1
_payment_id_counter = 1
_refund_id_counter = 1
_deposit_request_id_counter = 1


def get_next_payment_method_id() -> int:
    """Get next payment method ID."""
    global _payment_method_id_counter
    id = _payment_method_id_counter
    _payment_method_id_counter += 1
    return id


def get_next_payment_id() -> int:
    """Get next payment ID."""
    global _payment_id_counter
    id = _payment_id_counter
    _payment_id_counter += 1
    return id


def get_next_refund_id() -> int:
    """Get next refund ID."""
    global _refund_id_counter
    id = _refund_id_counter
    _refund_id_counter += 1
    return id


def get_next_deposit_request_id() -> int:
    """Get next deposit request ID."""
    global _deposit_request_id_counter
    id = _deposit_request_id_counter
    _deposit_request_id_counter += 1
    return id


__all__ = [
    "User",
    "Contact",
    "Lead",
    "Interaction",
    "AutoReplyRule",
    "PricebookItem",
    "Estimate",
    "Job",
    "Service",
    "Quote",
    "QuoteItem",
    "Asset",
    "ProposalTemplate",
    "LeadStatus",
    "InteractionType",
    "LeadSource",
    "QuoteStatus",
    "get_next_contact_id",
    "get_next_lead_id",
    "get_next_interaction_id",
    "get_next_auto_reply_rule_id",
    "get_next_pricebook_item_id",
    "get_next_estimate_id",
    "get_next_job_id",
    "get_next_service_id",
    "get_next_quote_id",
    "get_next_quote_item_id",
    "get_next_asset_id",
    "get_next_proposal_template_id",
    "get_next_availability_config_id",
    "get_next_appointment_id",
    "get_next_form_template_id",
    "get_next_form_submission_id",
    "get_next_followup_sequence_id",
    "get_next_followup_instance_id",
    "get_next_followup_task_id",
    "AvailabilityConfig",
    "Appointment",
    "FormField",
    "FormTemplate",
    "FormSubmission",
    "FollowUpStep",
    "FollowUpSequence",
    "FollowUpInstance",
    "FollowUpTask",
    "PackageItem",
    "Package",
    "get_next_package_id",
    "CalendarConnection",
    "CalendarEvent",
    "get_next_calendar_connection_id",
    "get_next_calendar_event_id",
    "SMSMessage",
    "SMSConversation",
    "SMSTemplate",
    "get_next_sms_message_id",
    "get_next_sms_conversation_id",
    "get_next_sms_template_id",
    "PaymentMethod",
    "Payment",
    "Refund",
    "DepositRequest",
    "get_next_payment_method_id",
    "get_next_payment_id",
    "get_next_refund_id",
    "get_next_deposit_request_id",
]
