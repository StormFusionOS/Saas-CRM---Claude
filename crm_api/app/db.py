"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
CRM API In-Memory Database for Testing.

PRODUCTION NOTE: Replace this with real SQLAlchemy session management:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, Session
    from app.core.config import settings

    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def get_db() -> Generator[Session, None, None]:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
"""

from typing import Generator, Optional
from datetime import datetime


# In-memory storage for testing
_users = []
_contacts = []
_leads = []
_interactions = []
_auto_reply_rules = []
_services = []
_quotes = []
_quote_items = []
_assets = {}  # Dict[int, Asset]
_proposal_templates = {}  # Dict[int, ProposalTemplate]
_availability_configs = {}  # Dict[int, AvailabilityConfig]
_appointments = []  # List[Appointment]
_form_templates = {}  # Dict[int, FormTemplate]
_form_submissions = []  # List[FormSubmission]
_followup_sequences = {}  # Dict[int, FollowUpSequence]
_followup_instances = []  # List[FollowUpInstance]
_followup_tasks = []  # List[FollowUpTask]
_packages = {}  # Dict[int, Package]
_calendar_connections = {}  # Dict[int, CalendarConnection]
_calendar_events = []  # List[CalendarEvent]
_sms_messages = []  # List[SMSMessage]
_sms_conversations = {}  # Dict[int, SMSConversation]
_sms_templates = {}  # Dict[int, SMSTemplate]
_payment_methods = {}  # Dict[int, PaymentMethod]
_payments = []  # List[Payment]
_refunds = []  # List[Refund]
_deposit_requests = []  # List[DepositRequest]


class InMemoryDB:
    """Simple in-memory database for testing."""

    def __init__(self):
        self.users = _users
        self.contacts = _contacts
        self.leads = _leads
        self.interactions = _interactions
        self.auto_reply_rules = _auto_reply_rules
        self.services = _services
        self.quotes = _quotes
        self.quote_items = _quote_items
        self.assets = _assets
        self.proposal_templates = _proposal_templates
        self.availability_configs = _availability_configs
        self.appointments = _appointments
        self.form_templates = _form_templates
        self.form_submissions = _form_submissions
        self.followup_sequences = _followup_sequences
        self.followup_instances = _followup_instances
        self.followup_tasks = _followup_tasks
        self.packages = _packages
        self.calendar_connections = _calendar_connections
        self.calendar_events = _calendar_events
        self.sms_messages = _sms_messages
        self.sms_conversations = _sms_conversations
        self.sms_templates = _sms_templates
        self.payment_methods = _payment_methods
        self.payments = _payments
        self.refunds = _refunds
        self.deposit_requests = _deposit_requests
        self._committed = True

    def add(self, obj):
        """Add object to appropriate collection."""
        from app.models import User, Contact, Lead, Interaction, AutoReplyRule, Service, Quote, QuoteItem

        if isinstance(obj, User):
            self.users.append(obj)
        elif isinstance(obj, Contact):
            self.contacts.append(obj)
        elif isinstance(obj, Lead):
            self.leads.append(obj)
        elif isinstance(obj, Interaction):
            self.interactions.append(obj)
        elif isinstance(obj, AutoReplyRule):
            self.auto_reply_rules.append(obj)
        elif isinstance(obj, Service):
            self.services.append(obj)
        elif isinstance(obj, Quote):
            self.quotes.append(obj)
        elif isinstance(obj, QuoteItem):
            self.quote_items.append(obj)

    def delete(self, obj):
        """Remove object from appropriate collection."""
        from app.models import User, Contact, Lead, Interaction, AutoReplyRule, Service, Quote, QuoteItem

        if isinstance(obj, User):
            self.users.remove(obj)
        elif isinstance(obj, Contact):
            self.contacts.remove(obj)
        elif isinstance(obj, Lead):
            self.leads.remove(obj)
        elif isinstance(obj, Interaction):
            self.interactions.remove(obj)
        elif isinstance(obj, AutoReplyRule):
            self.auto_reply_rules.remove(obj)
        elif isinstance(obj, Service):
            self.services.remove(obj)
        elif isinstance(obj, Quote):
            self.quotes.remove(obj)
        elif isinstance(obj, QuoteItem):
            self.quote_items.remove(obj)

    def commit(self):
        """Commit transaction (no-op in memory)."""
        self._committed = True

    def rollback(self):
        """Rollback transaction (no-op in memory)."""
        self._committed = False

    def close(self):
        """Close session (no-op in memory)."""
        pass

    def refresh(self, obj):
        """Refresh object (no-op in memory)."""
        pass

    def query(self, model):
        """Query helper."""
        from app.models import User, Contact, Lead, Interaction, AutoReplyRule, Service, Quote, QuoteItem

        if model == User:
            return QueryHelper(self.users)
        elif model == Contact:
            return QueryHelper(self.contacts)
        elif model == Lead:
            return QueryHelper(self.leads)
        elif model == Interaction:
            return QueryHelper(self.interactions)
        elif model == AutoReplyRule:
            return QueryHelper(self.auto_reply_rules)
        elif model == Service:
            return QueryHelper(self.services)
        elif model == Quote:
            return QueryHelper(self.quotes)
        elif model == QuoteItem:
            return QueryHelper(self.quote_items)
        else:
            return QueryHelper([])


class QueryHelper:
    """Simple query helper for in-memory collections."""

    def __init__(self, collection: list):
        self.collection = collection
        self._filters = []

    def filter(self, *args, **kwargs):
        """Add filter (simplified)."""
        # Store filter conditions
        for key, value in kwargs.items():
            self._filters.append((key, value))
        return self

    def filter_by(self, **kwargs):
        """Filter by exact match."""
        return self.filter(**kwargs)

    def first(self) -> Optional[object]:
        """Get first matching object."""
        results = self.all()
        return results[0] if results else None

    def all(self) -> list:
        """Get all matching objects."""
        results = self.collection.copy()

        # Apply filters
        for key, value in self._filters:
            results = [
                obj for obj in results
                if getattr(obj, key, None) == value
            ]

        return results

    def count(self) -> int:
        """Count matching objects."""
        return len(self.all())

    def one(self):
        """Get exactly one object (raises if not found or multiple)."""
        results = self.all()
        if len(results) == 0:
            raise Exception("No results found")
        if len(results) > 1:
            raise Exception("Multiple results found")
        return results[0]

    def one_or_none(self) -> Optional[object]:
        """Get one object or None."""
        results = self.all()
        if len(results) == 0:
            return None
        if len(results) > 1:
            raise Exception("Multiple results found")
        return results[0]


def get_db() -> Generator[InMemoryDB, None, None]:
    """
    Get database session.

    Yields:
        Database session
    """
    db = InMemoryDB()
    try:
        yield db
    finally:
        db.close()


def init_demo_data():
    """Initialize demo data for testing."""
    from app.models import User, Service, ProposalTemplate, Contact, Lead, LeadStatus, LeadSource, AvailabilityConfig
    from app.core.security import hash_password, Role

    # Clear existing data
    _users.clear()
    _contacts.clear()
    _leads.clear()
    _interactions.clear()
    _auto_reply_rules.clear()
    _services.clear()
    _quotes.clear()
    _quote_items.clear()
    _assets.clear()
    _proposal_templates.clear()
    _availability_configs.clear()
    _appointments.clear()
    _form_templates.clear()
    _form_submissions.clear()
    _followup_sequences.clear()
    _followup_instances.clear()
    _followup_tasks.clear()

    # Create demo users
    demo_users = [
        User(
            id=1,
            email="Nathan@RiverCityClean.com",
            hashed_password=hash_password("password123"),
            full_name="Nathan - Sales",
            roles=[Role.SALES.value],
            is_active=True,
            created_at=datetime.utcnow(),
        ),
        User(
            id=2,
            email="manager@rivercityclean.com",
            hashed_password=hash_password("password123"),
            full_name="Sales Manager",
            roles=[Role.SALES_MANAGER.value],
            is_active=True,
            created_at=datetime.utcnow(),
        ),
        User(
            id=3,
            email="owner@rivercityclean.com",
            hashed_password=hash_password("password123"),
            full_name="Owner",
            roles=[Role.OWNER.value],
            is_active=True,
            created_at=datetime.utcnow(),
        ),
    ]

    _users.extend(demo_users)

    # Create demo contact
    demo_contact = Contact(
        id=1,
        email="demo.customer@example.com",
        phone="555-123-4567",
        first_name="Demo",
        last_name="Customer",
        created_at=datetime.utcnow(),
    )
    _contacts.append(demo_contact)

    # Create demo lead
    demo_lead = Lead(
        id=1,
        contact_id=1,
        status=LeadStatus.NEW.value,
        source=LeadSource.MANUAL.value,
        assigned_to_id=1,  # Assigned to Nathan
        notes="Demo lead for testing",
        created_at=datetime.utcnow(),
    )
    _leads.append(demo_lead)

    # Create demo services
    demo_services = [
        Service(
            id=1,
            name="House Wash",
            description="Professional soft wash house cleaning service. Removes dirt, mold, and mildew from exterior surfaces.",
            category="house_wash",
            base_price=0.15,
            unit="sq_ft",
            min_price=199.00,
            pricing_formula="base_price * sq_ft",
            modifiers={
                "two_story": 1.3,
                "three_story": 1.5,
                "heavy_staining": 1.2
            },
            is_active=True,
            display_order=1,
            metadata={
                "typical_range": "2000-5000 sq ft",
                "duration": "2-4 hours",
                "eco_friendly": "true"
            },
            created_at=datetime.utcnow(),
        ),
        Service(
            id=2,
            name="Gutter Clean",
            description="Complete gutter cleaning and debris removal. Includes downspout flushing and minor clog clearing.",
            category="gutter_clean",
            base_price=1.50,
            unit="linear_ft",
            min_price=149.00,
            pricing_formula="base_price * linear_ft",
            modifiers={
                "two_story": 1.4,
                "three_story": 1.7,
                "heavily_clogged": 1.3
            },
            is_active=True,
            display_order=2,
            metadata={
                "typical_range": "100-300 linear ft",
                "duration": "1-3 hours",
                "includes_downspouts": "true"
            },
            created_at=datetime.utcnow(),
        ),
        Service(
            id=3,
            name="Window Clean",
            description="Interior and exterior window cleaning. Includes screens, sills, and frames.",
            category="window_clean",
            base_price=6.00,
            unit="each",
            min_price=99.00,
            pricing_formula="base_price * quantity",
            modifiers={
                "exterior_only": 0.6,
                "interior_only": 0.5,
                "hard_water_stains": 1.3
            },
            is_active=True,
            display_order=3,
            metadata={
                "typical_range": "15-40 windows",
                "duration": "2-4 hours",
                "includes_screens": "true"
            },
            created_at=datetime.utcnow(),
        ),
    ]

    _services.extend(demo_services)

    # Create default proposal template
    default_template = ProposalTemplate(
        id=1,
        name="Default Professional Template",
        description="Standard professional proposal template for all services",
        brand_primary_color="#0066cc",
        brand_secondary_color="#003366",
        header_html="""
            <div style="text-align: center; padding: 2rem;">
                <h1 style="color: var(--primary-color);">{{customer.first_name}}, here's your custom proposal</h1>
                <p style="font-size: 1.2rem; color: #666;">Proposal {{quote.number}}</p>
            </div>
        """,
        introduction_html="""
            <div style="padding: 2rem;">
                <h2>Dear {{customer.full_name}},</h2>
                <p>Thank you for considering RiverCityClean for your property care needs. We're excited to present this custom proposal for your project.</p>
                <p>Our team has carefully reviewed your requirements and put together a comprehensive solution that delivers exceptional results while respecting your budget.</p>
            </div>
        """,
        services_section_html="""
            <div style="padding: 2rem; background: #f9f9f9;">
                <h2 style="color: var(--primary-color);">Services Included</h2>
                <p>Your custom package includes the following professional services:</p>
                {{service.details}}
            </div>
        """,
        benefits_html="""
            <div style="padding: 2rem;">
                <h2 style="color: var(--primary-color);">Why Choose RiverCityClean?</h2>
                <ul style="list-style: none; padding: 0;">
                    <li style="padding: 0.5rem 0;">✓ <strong>Professional Excellence:</strong> Our experienced team delivers quality results every time</li>
                    <li style="padding: 0.5rem 0;">✓ <strong>Eco-Friendly Products:</strong> Safe for your family, pets, and the environment</li>
                    <li style="padding: 0.5rem 0;">✓ <strong>Satisfaction Guaranteed:</strong> We're not done until you're completely happy</li>
                    <li style="padding: 0.5rem 0;">✓ <strong>Fully Insured:</strong> Comprehensive liability and workers compensation coverage</li>
                    <li style="padding: 0.5rem 0;">✓ <strong>Transparent Pricing:</strong> No hidden fees or surprise charges</li>
                </ul>
            </div>
        """,
        scope_html="""
            <div style="padding: 2rem; background: #f9f9f9;">
                <h2 style="color: var(--primary-color);">Scope of Work</h2>
                <p>We will complete all services listed above to the highest professional standards. Our team will:</p>
                <ul>
                    <li>Arrive on time and prepared with all necessary equipment</li>
                    <li>Protect your property and landscaping throughout the process</li>
                    <li>Complete a thorough walkthrough with you upon completion</li>
                    <li>Clean up completely before we leave</li>
                </ul>
            </div>
        """,
        exclusions_html="""
            <div style="padding: 2rem;">
                <h2 style="color: var(--primary-color);">Not Included</h2>
                <p>The following items are not included in this proposal:</p>
                <ul>
                    <li>Repairs to damaged or deteriorated surfaces</li>
                    <li>Tree trimming or vegetation removal</li>
                    <li>Services not specifically listed above</li>
                </ul>
                <p><em>Additional services can be added at any time for an additional fee.</em></p>
            </div>
        """,
        terms_html="""
            <div style="padding: 2rem; background: #f9f9f9;">
                <h2 style="color: var(--primary-color);">Terms & Conditions</h2>
                <ul>
                    <li><strong>Pricing:</strong> The prices quoted in this proposal are valid until {{quote.valid_until}}</li>
                    <li><strong>Payment:</strong> Payment is due upon completion. We accept cash, check, and all major credit cards.</li>
                    <li><strong>Scheduling:</strong> Work will be scheduled within {{job.date_window}} of acceptance</li>
                    <li><strong>Weather:</strong> Services may be rescheduled due to inclement weather</li>
                    <li><strong>Guarantee:</strong> All work is guaranteed for 30 days</li>
                </ul>
            </div>
        """,
        footer_html="""
            <div style="padding: 2rem; text-align: center; color: #666;">
                <p>Questions? Call us at (555) 123-4567 or email info@rivercityclean.com</p>
                <p style="font-size: 0.9rem; margin-top: 1rem;">RiverCityClean Professional Services</p>
            </div>
        """,
        is_default=True,
        is_active=True,
        service_categories=[],  # Applies to all services
        package_tiers=[],  # Applies to all packages
        initialed_clauses=[
            {
                "id": "ladder_waiver",
                "title": "Ladder & Equipment Waiver",
                "text": "I understand that this service may require the use of ladders, lifts, or other equipment on my property. I agree to ensure safe access and waive RiverCityClean of liability for pre-existing property conditions that may be affected during normal service operations.",
                "required": True
            },
            {
                "id": "oxidation_disclaimer",
                "title": "Oxidation & Paint Condition Disclaimer",
                "text": "I understand that if my property's paint is oxidized, chalking, or in poor condition, the cleaning process may reveal or worsen these pre-existing conditions. This is not damage caused by the cleaning but rather the exposure of existing deterioration.",
                "required": False
            }
        ],
        created_at=datetime.utcnow(),
    )

    _proposal_templates[1] = default_template

    # Create default availability config
    default_availability = AvailabilityConfig(
        id=1,
        name="Default Business Hours",
        start_time="09:00",
        end_time="17:00",
        working_days=[1, 2, 3, 4, 5],  # Monday-Friday
        slot_duration_minutes=120,  # 2-hour slots
        buffer_minutes=30,
        max_appointments_per_day=4,
        min_notice_hours=24,
        max_days_advance=60,
        blackout_dates=["2025-12-25", "2025-01-01"],  # Christmas and New Year
        is_active=True,
        created_at=datetime.utcnow(),
    )

    _availability_configs[1] = default_availability

    # Create demo form templates
    from app.models import FormTemplate, FormField

    # Service intake form
    service_intake_form = FormTemplate(
        id=1,
        name="Service Intake Form",
        title="Property & Service Details",
        description="Help us understand your property and service needs",
        fields=[
            FormField(
                id="property_type",
                label="Property Type",
                field_type="select",
                options=["Residential", "Commercial", "Multi-Family"],
                required=True,
                order=1,
                width="half",
            ),
            FormField(
                id="property_size",
                label="Approximate Property Size (sq ft)",
                field_type="number",
                min_value=500,
                max_value=50000,
                required=True,
                placeholder="e.g., 2500",
                order=2,
                width="half",
            ),
            FormField(
                id="stories",
                label="Number of Stories",
                field_type="select",
                options=["1", "2", "3+"],
                required=True,
                order=3,
                width="half",
            ),
            FormField(
                id="service_frequency",
                label="How often would you like this service?",
                field_type="radio",
                options=["One-time", "Monthly", "Quarterly", "Semi-annually", "Annually"],
                required=True,
                order=4,
                width="full",
            ),
            FormField(
                id="specific_concerns",
                label="Specific Areas of Concern",
                field_type="multiselect",
                options=["Mold/Mildew", "Heavy Staining", "Roof Cleaning", "Gutters", "Windows", "Deck/Patio"],
                required=False,
                help_text="Select all that apply",
                order=5,
                width="full",
            ),
            FormField(
                id="additional_notes",
                label="Additional Notes or Questions",
                field_type="textarea",
                placeholder="Any specific details we should know about...",
                required=False,
                max_length=1000,
                order=6,
                width="full",
            ),
        ],
        is_active=True,
        attach_to_proposal=True,
        attach_to_quote=True,
        category="intake",
        tags=["service", "property", "initial"],
        send_confirmation_email=True,
        notify_staff_on_submission=True,
        notification_emails=["Nathan@RiverCityClean.com"],
        success_message="Thank you! We've received your property details and will include this in your quote.",
        created_at=datetime.utcnow(),
        created_by=1,
    )

    # Feedback form
    feedback_form = FormTemplate(
        id=2,
        name="Service Feedback",
        title="How Did We Do?",
        description="Your feedback helps us improve our service",
        fields=[
            FormField(
                id="overall_rating",
                label="Overall Satisfaction",
                field_type="select",
                options=["Excellent", "Good", "Fair", "Poor"],
                required=True,
                order=1,
                width="half",
            ),
            FormField(
                id="would_recommend",
                label="Would you recommend us to others?",
                field_type="radio",
                options=["Definitely", "Probably", "Not Sure", "Probably Not", "Definitely Not"],
                required=True,
                order=2,
                width="full",
            ),
            FormField(
                id="quality_rating",
                label="Quality of Work",
                field_type="select",
                options=["5 - Excellent", "4 - Good", "3 - Average", "2 - Below Average", "1 - Poor"],
                required=True,
                order=3,
                width="half",
            ),
            FormField(
                id="timeliness_rating",
                label="Timeliness",
                field_type="select",
                options=["5 - Excellent", "4 - Good", "3 - Average", "2 - Below Average", "1 - Poor"],
                required=True,
                order=4,
                width="half",
            ),
            FormField(
                id="communication_rating",
                label="Communication",
                field_type="select",
                options=["5 - Excellent", "4 - Good", "3 - Average", "2 - Below Average", "1 - Poor"],
                required=True,
                order=5,
                width="half",
            ),
            FormField(
                id="feedback_comments",
                label="Additional Comments",
                field_type="textarea",
                placeholder="Tell us what we did well or how we could improve...",
                required=False,
                max_length=1000,
                order=6,
                width="full",
            ),
        ],
        is_active=True,
        attach_to_proposal=False,
        attach_to_quote=False,
        category="feedback",
        tags=["feedback", "satisfaction", "post-service"],
        send_confirmation_email=True,
        notify_staff_on_submission=True,
        notification_emails=["manager@rivercityclean.com"],
        success_message="Thank you for your feedback! We truly appreciate your time.",
        created_at=datetime.utcnow(),
        created_by=1,
    )

    _form_templates[1] = service_intake_form
    _form_templates[2] = feedback_form

    # Create demo follow-up sequences
    from app.models import FollowUpSequence, FollowUpStep

    # New Lead Nurture Sequence
    new_lead_sequence = FollowUpSequence(
        id=1,
        name="New Lead Nurture - 7 Day",
        description="Automated 7-day follow-up sequence for new leads",
        trigger_event="lead_created",
        trigger_conditions={"lead_status": "NEW"},
        steps=[
            FollowUpStep(
                id="welcome_email",
                order=1,
                delay_hours=1,  # 1 hour after lead created
                action_type="email",
                subject="Welcome to RiverCityClean!",
                body_template="Hi {{first_name}},\n\nThank you for your interest in RiverCityClean! We're excited to help keep your property looking its best.\n\nI'll follow up with you shortly to discuss your needs.\n\nBest regards,\nThe RiverCityClean Team",
            ),
            FollowUpStep(
                id="day_2_call_task",
                order=2,
                delay_hours=48,  # 2 days after lead created
                action_type="task",
                task_title="Call new lead: {{first_name}} {{last_name}}",
                task_description="Follow up on initial inquiry. Discuss property details and service needs.",
                assign_to_role="SALES",
            ),
            FollowUpStep(
                id="day_5_email",
                order=3,
                delay_hours=120,  # 5 days
                action_type="email",
                subject="Quick question about your property",
                body_template="Hi {{first_name}},\n\nI wanted to check in and see if you had any questions about our services.\n\nMany homeowners appreciate knowing:\n- We use eco-friendly cleaning solutions\n- Average service takes 2-4 hours\n- Free quotes with no obligation\n\nWould you like to schedule a free consultation?\n\nBest,\nRiverCityClean",
                skip_if_responded=True,
            ),
            FollowUpStep(
                id="day_7_final_touchpoint",
                order=4,
                delay_hours=168,  # 7 days
                action_type="task",
                task_title="Final follow-up: {{first_name}} {{last_name}}",
                task_description="Last touchpoint for this lead. If no response, move to cold status.",
                assign_to_role="SALES",
                skip_if_responded=True,
            ),
        ],
        is_active=True,
        stop_on_response=True,
        stop_on_status_change=True,
        stop_statuses=["QUALIFIED", "LOST", "CONVERTED"],
        category="nurture",
        tags=["new_lead", "automated", "7_day"],
        created_at=datetime.utcnow(),
        created_by=1,
    )

    # Quote Follow-Up Sequence
    quote_followup_sequence = FollowUpSequence(
        id=2,
        name="Quote Follow-Up",
        description="Follow up on sent quotes to increase conversion",
        trigger_event="quote_sent",
        steps=[
            FollowUpStep(
                id="day_1_check_in",
                order=1,
                delay_hours=24,  # 1 day after quote sent
                action_type="email",
                subject="Question about your quote?",
                body_template="Hi {{first_name}},\n\nI wanted to check if you had a chance to review the quote I sent yesterday.\n\nDo you have any questions about:\n- Our pricing\n- The scope of work\n- Our availability\n\nI'm here to help!\n\nBest,\nRiverCityClean",
            ),
            FollowUpStep(
                id="day_3_call",
                order=2,
                delay_hours=72,  # 3 days
                action_type="task",
                task_title="Follow up on quote: {{company_name}}",
                task_description="Call to discuss quote. Address any concerns. Try to close the deal.",
                assign_to_role="SALES",
                skip_if_responded=True,
            ),
            FollowUpStep(
                id="day_7_last_chance",
                order=3,
                delay_hours=168,  # 7 days
                action_type="email",
                subject="Your quote expires soon",
                body_template="Hi {{first_name}},\n\nJust a quick reminder that your quote will expire in a few days.\n\nIf you'd like to move forward or have questions, please let me know!\n\nWe'd love to work with you.\n\nBest,\nRiverCityClean",
                skip_if_responded=True,
            ),
        ],
        is_active=True,
        stop_on_response=True,
        category="follow_up",
        tags=["quote", "conversion"],
        created_at=datetime.utcnow(),
        created_by=1,
    )

    _followup_sequences[1] = new_lead_sequence
    _followup_sequences[2] = quote_followup_sequence

    # ========================================================================
    # Packages & Bundles
    # ========================================================================

    from app.models import Package, PackageItem, get_next_package_id

    # Package 1: Spring Cleanup Bundle
    spring_cleanup = Package(
        id=get_next_package_id(),
        name="Spring Cleanup Special",
        description="Complete spring cleanup package - get your property ready for the season!",
        category="seasonal",
        items=[
            PackageItem(pricebook_item_id=1, quantity=1, display_order=1),  # Lawn Cleanup
            PackageItem(pricebook_item_id=2, quantity=1, display_order=2),  # Hedge Trimming
            PackageItem(pricebook_item_id=3, quantity=1, display_order=3),  # Mulching
            PackageItem(pricebook_item_id=4, quantity=1, display_order=4, is_optional=True),  # Fertilization (optional)
        ],
        pricing_type="calculated",
        discount_percent=15.0,
        is_active=True,
        valid_from=datetime(2025, 3, 1),
        valid_to=datetime(2025, 5, 31),
        featured=True,
        tags=["seasonal", "spring", "cleanup", "popular"],
        terms="Package must be scheduled within validity period. Weather delays possible.",
        requires_site_visit=False,
        display_order=1,
        created_at=datetime.utcnow(),
        created_by=1,
    )

    # Package 2: Monthly Maintenance
    monthly_maintenance = Package(
        id=get_next_package_id(),
        name="Monthly Maintenance Package",
        description="Recurring monthly service to keep your property looking great year-round",
        category="maintenance",
        items=[
            PackageItem(pricebook_item_id=5, quantity=1, display_order=1),  # Lawn Mowing
            PackageItem(pricebook_item_id=6, quantity=1, display_order=2),  # Edging
            PackageItem(pricebook_item_id=7, quantity=1, display_order=3),  # Blowing/Cleanup
        ],
        pricing_type="fixed",
        fixed_price=129.99,
        is_active=True,
        featured=True,
        tags=["maintenance", "recurring", "popular"],
        terms="Monthly recurring service. 3-month minimum commitment. Cancel anytime after.",
        requires_site_visit=True,
        display_order=2,
        created_at=datetime.utcnow(),
        created_by=1,
    )

    # Package 3: Fall Cleanup Bundle
    fall_cleanup = Package(
        id=get_next_package_id(),
        name="Fall Cleanup Bundle",
        description="Prepare your property for winter with our comprehensive fall package",
        category="seasonal",
        items=[
            PackageItem(pricebook_item_id=8, quantity=1, display_order=1),  # Leaf Removal
            PackageItem(pricebook_item_id=9, quantity=1, display_order=2),  # Gutter Cleaning
            PackageItem(pricebook_item_id=3, quantity=1, display_order=3),  # Mulching
            PackageItem(pricebook_item_id=10, quantity=1, display_order=4),  # Winterization
        ],
        pricing_type="calculated",
        discount_percent=20.0,
        is_active=True,
        valid_from=datetime(2025, 9, 1),
        valid_to=datetime(2025, 11, 30),
        featured=False,
        tags=["seasonal", "fall", "cleanup"],
        terms="Best value when booked early. Weather delays possible.",
        requires_site_visit=False,
        display_order=3,
        created_at=datetime.utcnow(),
        created_by=1,
    )

    _packages[spring_cleanup.id] = spring_cleanup
    _packages[monthly_maintenance.id] = monthly_maintenance
    _packages[fall_cleanup.id] = fall_cleanup

    # ========================================================================
    # Calendar Connections
    # ========================================================================

    from app.models import CalendarConnection, CalendarEvent, get_next_calendar_connection_id, get_next_calendar_event_id

    # Demo calendar connection for Nathan (user_id=1)
    google_calendar = CalendarConnection(
        id=get_next_calendar_connection_id(),
        user_id=1,
        provider="google",
        calendar_id="nathan@rivercityclean.com_primary",
        calendar_name="Nathan's Calendar",
        access_token="mock_access_token_12345",  # In production, this would be encrypted
        refresh_token="mock_refresh_token_67890",
        token_expires_at=datetime(2025, 12, 31),
        is_active=True,
        sync_enabled=True,
        sync_direction="bidirectional",
        auto_sync=True,
        sync_interval_minutes=15,
        last_sync_at=datetime.utcnow(),
        last_sync_status="success",
        events_synced=5,
        sync_failures=0,
        created_at=datetime.utcnow(),
    )

    # Demo Outlook calendar connection
    outlook_calendar = CalendarConnection(
        id=get_next_calendar_connection_id(),
        user_id=1,
        provider="outlook",
        calendar_id="AAMkAGI2THVSAAA=",
        calendar_name="Work Calendar",
        access_token="mock_outlook_token_abc",
        refresh_token="mock_outlook_refresh_xyz",
        token_expires_at=datetime(2025, 12, 31),
        is_active=True,
        sync_enabled=False,  # Disabled for now
        sync_direction="push",  # Only push events to Outlook
        auto_sync=False,
        sync_interval_minutes=30,
        last_sync_at=None,
        last_sync_status="",
        events_synced=0,
        sync_failures=0,
        created_at=datetime.utcnow(),
    )

    _calendar_connections[google_calendar.id] = google_calendar
    _calendar_connections[outlook_calendar.id] = outlook_calendar

    # Demo synced events (assuming some appointments exist)
    # In a real scenario, these would be created when appointments are made
    demo_event = CalendarEvent(
        id=get_next_calendar_event_id(),
        connection_id=google_calendar.id,
        appointment_id=1,  # Assumes appointment ID 1 exists
        external_event_id="google_event_123abc",
        title="Property Inspection - Smith Residence",
        start_time=datetime(2025, 11, 10, 10, 0),
        end_time=datetime(2025, 11, 10, 11, 0),
        location="123 Main St, Richmond, VA",
        description="Initial property inspection for quote",
        sync_status="synced",
        last_synced_at=datetime.utcnow(),
        attendees=["john.smith@example.com"],
        created_at=datetime.utcnow(),
    )

    _calendar_events.append(demo_event)

    # ========================================================================
    # SMS / Text Hub Demo Data
    # ========================================================================
    from app.models import (
        SMSMessage,
        SMSConversation,
        SMSTemplate,
        get_next_sms_message_id,
        get_next_sms_conversation_id,
        get_next_sms_template_id,
    )

    # SMS Templates
    appointment_reminder = SMSTemplate(
        id=get_next_sms_template_id(),
        name="Appointment Reminder",
        category="scheduling",
        body="Hi {{first_name}}! This is a reminder about your appointment on {{appointment_date}} at {{appointment_time}}. Reply YES to confirm or CANCEL to reschedule.",
        is_active=True,
        variables=["first_name", "appointment_date", "appointment_time"],
        created_at=datetime.utcnow(),
    )
    _sms_templates[appointment_reminder.id] = appointment_reminder

    quote_followup = SMSTemplate(
        id=get_next_sms_template_id(),
        name="Quote Follow-Up",
        category="sales",
        body="Hi {{first_name}}, just wanted to check if you had any questions about the quote we sent for {{service_type}}? We're here to help!",
        is_active=True,
        variables=["first_name", "service_type"],
        created_at=datetime.utcnow(),
    )
    _sms_templates[quote_followup.id] = quote_followup

    thank_you = SMSTemplate(
        id=get_next_sms_template_id(),
        name="Thank You After Service",
        category="customer_service",
        body="Thank you for choosing RiverCityClean, {{first_name}}! We hope you're happy with our work. Reply REVIEW to leave us feedback!",
        is_active=True,
        variables=["first_name"],
        created_at=datetime.utcnow(),
    )
    _sms_templates[thank_you.id] = thank_you

    # SMS Conversations (assuming contact ID 1 = John Smith)
    conversation_1 = SMSConversation(
        id=get_next_sms_conversation_id(),
        contact_id=1,  # John Smith
        phone_number="+15551234567",
        status="active",
        message_count=3,
        unread_count=0,
        last_message_at=datetime(2025, 11, 3, 14, 30),
        assigned_to=1,  # Nathan (user ID 1)
        created_at=datetime(2025, 11, 1, 10, 0),
    )
    _sms_conversations[conversation_1.id] = conversation_1

    # SMS Messages
    msg1 = SMSMessage(
        id=get_next_sms_message_id(),
        conversation_id=conversation_1.id,
        contact_id=1,
        lead_id=1,
        from_number="+18045551234",  # Business number
        to_number="+15551234567",
        body="Hi John! This is Nathan from RiverCityClean. Thanks for your interest in our lawn care services. When would be a good time for a quote?",
        direction="outbound",
        status="delivered",
        provider="twilio",
        provider_message_id="SM1234567890abcdef",
        sent_at=datetime(2025, 11, 1, 10, 0),
        delivered_at=datetime(2025, 11, 1, 10, 0, 5),
        sent_by=1,
        created_at=datetime(2025, 11, 1, 10, 0),
    )
    _sms_messages.append(msg1)

    msg2 = SMSMessage(
        id=get_next_sms_message_id(),
        conversation_id=conversation_1.id,
        contact_id=1,
        lead_id=1,
        from_number="+15551234567",
        to_number="+18045551234",
        body="Hi Nathan! I'm available tomorrow afternoon. Does 2pm work?",
        direction="inbound",
        status="received",
        provider="twilio",
        provider_message_id="SM0987654321fedcba",
        sent_at=datetime(2025, 11, 1, 14, 30),
        delivered_at=datetime(2025, 11, 1, 14, 30),
        created_at=datetime(2025, 11, 1, 14, 30),
    )
    _sms_messages.append(msg2)

    msg3 = SMSMessage(
        id=get_next_sms_message_id(),
        conversation_id=conversation_1.id,
        contact_id=1,
        lead_id=1,
        from_number="+18045551234",
        to_number="+15551234567",
        body="Perfect! I've scheduled you for tomorrow at 2pm. Looking forward to meeting you!",
        direction="outbound",
        status="delivered",
        provider="twilio",
        provider_message_id="SM1111222233334444",
        sent_at=datetime(2025, 11, 3, 14, 30),
        delivered_at=datetime(2025, 11, 3, 14, 30, 3),
        sent_by=1,
        created_at=datetime(2025, 11, 3, 14, 30),
    )
    _sms_messages.append(msg3)


# Initialize demo data on module load
init_demo_data()


__all__ = ["get_db", "InMemoryDB", "init_demo_data"]
