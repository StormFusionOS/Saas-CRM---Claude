#!/usr/bin/env python3
"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Database Seeding Script

Seeds demo data for local development:
- CRM: Contacts, Leads, Interactions
- Ops: Alerts, Service Health checks, Task runs

Usage:
    python scripts/seed.py              # Seed all
    python scripts/seed.py --crm        # Seed CRM only
    python scripts/seed.py --ops        # Seed Ops only
    python scripts/seed.py --clear      # Clear all data
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import argparse

# Add project root to path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "crm_api"))
sys.path.insert(0, str(ROOT_DIR / "ops_api"))


def seed_crm_data():
    """Seed CRM database with demo data."""
    print("🌱 Seeding CRM data...")

    from crm_api.app.db import get_db, _contacts, _leads, _interactions
    from crm_api.app.models import (
        Contact,
        Lead,
        Interaction,
        get_next_contact_id,
        get_next_lead_id,
        get_next_interaction_id,
    )

    # Clear existing demo data (keep users)
    _contacts.clear()
    _leads.clear()
    _interactions.clear()

    # Create demo contacts
    contacts_data = [
        {
            "email": "john.smith@acmecorp.com",
            "first_name": "John",
            "last_name": "Smith",
            "company": "Acme Corporation",
            "title": "VP of Operations",
            "phone": "+1-555-0100",
            "tags": ["enterprise", "hot-lead"],
        },
        {
            "email": "sarah.johnson@techstartup.io",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "company": "Tech Startup Inc",
            "title": "CEO",
            "phone": "+1-555-0101",
            "tags": ["startup", "referral"],
        },
        {
            "email": "mike.chen@globalinc.com",
            "first_name": "Mike",
            "last_name": "Chen",
            "company": "Global Inc",
            "title": "Director of IT",
            "phone": "+1-555-0102",
            "tags": ["enterprise", "qualified"],
        },
        {
            "email": "emily.rodriguez@boutique.com",
            "first_name": "Emily",
            "last_name": "Rodriguez",
            "company": "Boutique Solutions",
            "phone": "+1-555-0103",
            "tags": ["smb"],
        },
        {
            "email": "david.kim@innovate.co",
            "first_name": "David",
            "last_name": "Kim",
            "company": "Innovate Co",
            "title": "CTO",
            "phone": "+1-555-0104",
            "tags": ["tech", "warm-lead"],
        },
    ]

    created_contacts = []
    for data in contacts_data:
        contact = Contact(
            id=get_next_contact_id(),
            created_at=datetime.utcnow() - timedelta(days=30),
            **data
        )
        _contacts.append(contact)
        created_contacts.append(contact)
        print(f"  ✓ Created contact: {contact.full_name} ({contact.company})")

    # Create demo leads
    lead_statuses = ["NEW", "CONTACTED", "QUALIFIED", "NEW", "CONTACTED"]

    for i, contact in enumerate(created_contacts):
        lead = Lead(
            id=get_next_lead_id(),
            contact_id=contact.id,
            status=lead_statuses[i],
            source="MANUAL" if i % 2 == 0 else "FACEBOOK",
            value=10000 + (i * 5000),
            probability=20 + (i * 15),
            notes=f"Demo lead for {contact.full_name}",
            created_at=datetime.utcnow() - timedelta(days=25 - i * 2),
        )
        _leads.append(lead)
        print(f"  ✓ Created lead: {contact.full_name} - Status: {lead.status}")

        # Create interactions for each lead
        interactions_count = 2 if i % 2 == 0 else 3
        for j in range(interactions_count):
            interaction = Interaction(
                id=get_next_interaction_id(),
                contact_id=contact.id,
                lead_id=lead.id,
                interaction_type="EMAIL" if j % 2 == 0 else "PHONE",
                direction="INBOUND" if j == 0 else "OUTBOUND",
                subject=f"Follow-up #{j+1}" if j > 0 else "Initial inquiry",
                body=f"Demo interaction #{j+1} with {contact.full_name}",
                created_at=datetime.utcnow() - timedelta(days=20 - i * 2 - j),
            )
            _interactions.append(interaction)

    print(f"✅ CRM: Created {len(_contacts)} contacts, {len(_leads)} leads, {len(_interactions)} interactions")


def seed_ops_data():
    """Seed Ops database with demo data."""
    print("🌱 Seeding Ops data...")

    from ops_api.app.db import _alerts, _service_health
    from ops_api.app.models.alert import Alert
    from ops_api.app.models.service_health import ServiceHealth

    # Clear existing demo data
    _alerts.clear()
    _service_health.clear()

    # Create demo alerts
    alerts_data = [
        {
            "id": 1,
            "severity": "HIGH",
            "message": "Database connection pool exhausted",
            "source": "monitoring",
            "created_at": datetime.utcnow() - timedelta(hours=2),
            "resolved": False,
        },
        {
            "id": 2,
            "severity": "MEDIUM",
            "message": "High memory usage detected on app server",
            "source": "monitoring",
            "created_at": datetime.utcnow() - timedelta(hours=5),
            "resolved": True,
        },
        {
            "id": 3,
            "severity": "LOW",
            "message": "SSL certificate expires in 30 days",
            "source": "security_scan",
            "created_at": datetime.utcnow() - timedelta(days=1),
            "resolved": False,
        },
    ]

    for data in alerts_data:
        alert = Alert(**data)
        _alerts.append(alert)
        status = "✓ RESOLVED" if alert.resolved else "⚠ OPEN"
        print(f"  {status} [{alert.severity}] {alert.message}")

    # Create demo service health checks
    services_data = [
        {
            "id": 1,
            "service_name": "crm-api",
            "status": "UP",
            "last_check": datetime.utcnow(),
            "response_time_ms": 45.2,
        },
        {
            "id": 2,
            "service_name": "ops-api",
            "status": "UP",
            "last_check": datetime.utcnow(),
            "response_time_ms": 38.7,
        },
        {
            "id": 3,
            "service_name": "crm-db",
            "status": "UP",
            "last_check": datetime.utcnow(),
            "response_time_ms": 12.1,
        },
        {
            "id": 4,
            "service_name": "ops-db",
            "status": "UP",
            "last_check": datetime.utcnow(),
            "response_time_ms": 15.3,
        },
        {
            "id": 5,
            "service_name": "redis",
            "status": "UP",
            "last_check": datetime.utcnow(),
            "response_time_ms": 2.8,
        },
    ]

    for data in services_data:
        health = ServiceHealth(**data)
        _service_health.append(health)
        print(f"  ✓ Service: {health.service_name} - {health.status} ({health.response_time_ms}ms)")

    print(f"✅ Ops: Created {len(_alerts)} alerts, {len(_service_health)} service health records")


def clear_all_data():
    """Clear all demo data."""
    print("🗑️  Clearing all data...")

    from crm_api.app.db import _contacts, _leads, _interactions
    from ops_api.app.db import _alerts, _service_health

    _contacts.clear()
    _leads.clear()
    _interactions.clear()
    _alerts.clear()
    _service_health.clear()

    print("✅ All data cleared")


def main():
    parser = argparse.ArgumentParser(description="Seed demo data")
    parser.add_argument("--crm", action="store_true", help="Seed CRM data only")
    parser.add_argument("--ops", action="store_true", help="Seed Ops data only")
    parser.add_argument("--clear", action="store_true", help="Clear all data")

    args = parser.parse_args()

    print("=" * 70)
    print("  Database Seeding Script")
    print("=" * 70)
    print()

    if args.clear:
        clear_all_data()
    elif args.crm:
        seed_crm_data()
    elif args.ops:
        seed_ops_data()
    else:
        # Seed all by default
        seed_crm_data()
        print()
        seed_ops_data()

    print()
    print("=" * 70)
    print("  ✅ Seeding Complete!")
    print("=" * 70)
    print()
    print("  Demo Credentials:")
    print("    Email:    Nathan@RiverCityClean.com")
    print("    Password: password123")
    print()


if __name__ == "__main__":
    main()
