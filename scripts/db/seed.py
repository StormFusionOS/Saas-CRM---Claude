#!/usr/bin/env python3
"""
Database Seeding Script.

Seeds minimal demo data for CRM and Ops APIs.
Works with both in-memory (test) and real database environments.

CRM Data:
- 10 Contacts
- 8 Leads with varied statuses
- 1-3 Interactions per lead

Ops Data:
- 5 tasks
- 3 backup runs
- 1 anomaly → suggestion workflow
"""

import argparse
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

# Add project and service directories to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "crm_api"))
sys.path.insert(0, str(project_root / "ops_api"))


class DataSeeder:
    """Seeds demo data into CRM and Ops databases."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.seed_log: List[Dict[str, Any]] = []

    def log(self, category: str, message: str, ids: List[int] = None):
        """Log seeded data."""
        entry = {
            "category": category,
            "message": message,
            "ids": ids or [],
            "timestamp": datetime.utcnow().isoformat()
        }
        self.seed_log.append(entry)

        if self.verbose:
            id_str = f" (IDs: {', '.join(map(str, ids))})" if ids else ""
            print(f"  ✓ {message}{id_str}")

    def seed_crm(self) -> bool:
        """Seed CRM database."""
        try:
            # Import CRM models and enums first
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / "crm_api"))
            from app.models import (
                Contact, Lead, Interaction,
                LeadStatus, InteractionType, LeadSource,
                get_next_contact_id, get_next_lead_id, get_next_interaction_id
            )
            from app.db import _contacts, _leads, _interactions, _users

            print("\n" + "="*80)
            print("SEEDING CRM DATABASE")
            print("="*80)

            # Clear existing data
            _contacts.clear()
            _leads.clear()
            _interactions.clear()

            # Seed 10 Contacts
            contact_ids = []
            contacts_data = [
                {
                    "first_name": "Alice", "last_name": "Johnson",
                    "email": "alice.johnson@example.com", "phone": "+1-555-0101",
                    "company": "TechStart Inc", "title": "CTO"
                },
                {
                    "first_name": "Bob", "last_name": "Smith",
                    "email": "bob.smith@acme.com", "phone": "+1-555-0102",
                    "company": "Acme Corp", "title": "CEO"
                },
                {
                    "first_name": "Carol", "last_name": "Davis",
                    "email": "carol.davis@innovate.io", "phone": "+1-555-0103",
                    "company": "Innovate.io", "title": "VP of Sales"
                },
                {
                    "first_name": "David", "last_name": "Wilson",
                    "email": "david.wilson@enterprise.com", "phone": "+1-555-0104",
                    "company": "Enterprise LLC", "title": "Director"
                },
                {
                    "first_name": "Emma", "last_name": "Martinez",
                    "email": "emma.martinez@startup.co", "phone": "+1-555-0105",
                    "company": "Startup.co", "title": "Founder"
                },
                {
                    "first_name": "Frank", "last_name": "Taylor",
                    "email": "frank.taylor@bigcorp.com", "phone": "+1-555-0106",
                    "company": "BigCorp", "title": "Manager"
                },
                {
                    "first_name": "Grace", "last_name": "Lee",
                    "email": "grace.lee@growth.io", "phone": "+1-555-0107",
                    "company": "Growth.io", "title": "Marketing Lead"
                },
                {
                    "first_name": "Henry", "last_name": "Brown",
                    "email": "henry.brown@scale.com", "phone": "+1-555-0108",
                    "company": "Scale Inc", "title": "Operations"
                },
                {
                    "first_name": "Iris", "last_name": "Chen",
                    "email": "iris.chen@ventures.com", "phone": "+1-555-0109",
                    "company": "Ventures LLC", "title": "Partner"
                },
                {
                    "first_name": "Jack", "last_name": "Anderson",
                    "email": "jack.anderson@consulting.com", "phone": "+1-555-0110",
                    "company": "Consulting Group", "title": "Senior Consultant"
                },
            ]

            for data in contacts_data:
                contact = Contact(
                    id=get_next_contact_id(),
                    **data,
                    tags=["demo", "seed"],
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 90))
                )
                _contacts.append(contact)
                contact_ids.append(contact.id)

            self.log("CRM", f"Seeded {len(contact_ids)} contacts", contact_ids)

            # Seed 8 Leads with varied statuses
            lead_ids = []
            lead_statuses = [
                LeadStatus.NEW,
                LeadStatus.NEW,
                LeadStatus.CONTACTED,
                LeadStatus.CONTACTED,
                LeadStatus.CONTACTED,
                LeadStatus.QUALIFIED,
                LeadStatus.WON,
                LeadStatus.LOST,
            ]

            lead_sources = [
                LeadSource.FACEBOOK,
                LeadSource.GOOGLE,
                LeadSource.TWILIO,
                LeadSource.MANUAL,
                LeadSource.FACEBOOK,
                LeadSource.GOOGLE,
                LeadSource.MANUAL,
                LeadSource.TWILIO,
            ]

            # Get manager user ID (assuming user with ID 2 is manager)
            manager_id = 2

            for i, (status, source) in enumerate(zip(lead_statuses, lead_sources)):
                contact_id = contact_ids[i]
                lead = Lead(
                    id=get_next_lead_id(),
                    contact_id=contact_id,
                    status=status.value,
                    source=source.value,
                    value=random.uniform(5000, 50000) if random.random() > 0.3 else None,
                    assigned_to_id=manager_id if random.random() > 0.3 else None,
                    probability=self._get_probability_for_status(status),
                    expected_close_date=datetime.utcnow() + timedelta(days=random.randint(7, 90)),
                    notes=f"Demo lead from {source.value}",
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60)),
                )
                _leads.append(lead)
                lead_ids.append(lead.id)

            self.log("CRM", f"Seeded {len(lead_ids)} leads", lead_ids)

            # Seed 1-3 Interactions per lead
            interaction_ids = []
            interaction_types = [
                InteractionType.EMAIL,
                InteractionType.SMS,
                InteractionType.PHONE,
                InteractionType.MEETING,
                InteractionType.NOTE,
                InteractionType.WEBHOOK,
            ]

            for lead in _leads:
                num_interactions = random.randint(1, 3)
                for _ in range(num_interactions):
                    interaction_type = random.choice(interaction_types)
                    direction = random.choice(["INBOUND", "OUTBOUND"])

                    interaction = Interaction(
                        id=get_next_interaction_id(),
                        contact_id=lead.contact_id,
                        lead_id=lead.id,
                        user_id=manager_id if direction == "OUTBOUND" else None,
                        interaction_type=interaction_type.value,
                        direction=direction,
                        subject=f"{interaction_type.value} interaction",
                        body=f"Demo {interaction_type.value.lower()} content for lead {lead.id}",
                        metadata={"demo": True, "source": "seed"},
                        created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                    )
                    _interactions.append(interaction)
                    interaction_ids.append(interaction.id)

            self.log("CRM", f"Seeded {len(interaction_ids)} interactions", interaction_ids)

            print(f"\n✅ CRM seeding completed successfully")
            print(f"   Contacts: {len(contact_ids)}")
            print(f"   Leads: {len(lead_ids)}")
            print(f"   Interactions: {len(interaction_ids)}")

            return True

        except Exception as e:
            print(f"❌ CRM seeding failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _get_probability_for_status(self, status) -> int:
        """Get probability percentage based on lead status."""
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "crm_api"))
        from app.models import LeadStatus

        probability_map = {
            LeadStatus.NEW: 10,
            LeadStatus.CONTACTED: 25,
            LeadStatus.QUALIFIED: 60,
            LeadStatus.WON: 100,
            LeadStatus.LOST: 0,
        }
        return probability_map.get(status, 0)

    def seed_ops(self) -> bool:
        """Seed Ops database."""
        try:
            # Import Ops models (reset path to avoid conflicts with CRM)
            ops_path = str(Path(__file__).parent.parent.parent / "ops_api")
            if ops_path not in sys.path:
                sys.path.insert(0, ops_path)

            # Remove CRM path if it exists to avoid conflicts
            crm_path = str(Path(__file__).parent.parent.parent / "crm_api")
            if crm_path in sys.path:
                sys.path.remove(crm_path)

            # Clear cached modules to force fresh import
            modules_to_remove = [k for k in sys.modules.keys() if k.startswith('app.')]
            for mod in modules_to_remove:
                del sys.modules[mod]

            from app.db import (
                _task_runs, _backup_runs, _suggestions,
                _alerts, _service_health
            )

            print("\n" + "="*80)
            print("SEEDING OPS DATABASE")
            print("="*80)

            # Clear existing data
            _task_runs.clear()
            _backup_runs.clear()
            _suggestions.clear()
            _alerts.clear()
            _service_health.clear()

            # Seed 5 task runs
            from dataclasses import dataclass, field
            from datetime import datetime

            @dataclass
            class TaskRun:
                id: int
                task_name: str
                status: str
                started_at: datetime
                completed_at: datetime
                duration_seconds: float
                result: dict = field(default_factory=dict)

            task_ids = []
            tasks = [
                {
                    "task_name": "backup_databases",
                    "status": "completed",
                    "duration_seconds": 120.5,
                    "result": {"files_backed_up": 3, "size_mb": 450}
                },
                {
                    "task_name": "check_service_health",
                    "status": "completed",
                    "duration_seconds": 5.2,
                    "result": {"services_checked": 8, "all_healthy": True}
                },
                {
                    "task_name": "generate_ai_suggestions",
                    "status": "completed",
                    "duration_seconds": 45.8,
                    "result": {"suggestions_generated": 3, "models_used": ["gpt-4"]}
                },
                {
                    "task_name": "scan_file_integrity",
                    "status": "completed",
                    "duration_seconds": 30.1,
                    "result": {"files_scanned": 1250, "anomalies": 1}
                },
                {
                    "task_name": "cleanup_old_logs",
                    "status": "running",
                    "duration_seconds": 0,
                    "result": {}
                },
            ]

            for i, task_data in enumerate(tasks):
                started_at = datetime.utcnow() - timedelta(hours=random.randint(1, 24))
                completed_at = started_at + timedelta(seconds=task_data["duration_seconds"]) \
                    if task_data["status"] == "completed" else None

                task_run = TaskRun(
                    id=i + 1,
                    task_name=task_data["task_name"],
                    status=task_data["status"],
                    started_at=started_at,
                    completed_at=completed_at,
                    duration_seconds=task_data["duration_seconds"],
                    result=task_data["result"]
                )
                _task_runs.append(task_run)
                task_ids.append(task_run.id)

            self.log("OPS", f"Seeded {len(task_ids)} task runs", task_ids)

            # Seed 3 backup runs
            @dataclass
            class BackupRun:
                id: int
                backup_type: str
                status: str
                started_at: datetime
                completed_at: datetime
                size_mb: float
                location: str

            backup_ids = []
            backups = [
                {
                    "backup_type": "full",
                    "status": "completed",
                    "size_mb": 1250.5,
                    "location": "s3://backups/full/2025-11-01.tar.gz"
                },
                {
                    "backup_type": "incremental",
                    "status": "completed",
                    "size_mb": 85.2,
                    "location": "s3://backups/incremental/2025-11-02.tar.gz"
                },
                {
                    "backup_type": "incremental",
                    "status": "completed",
                    "size_mb": 92.8,
                    "location": "s3://backups/incremental/2025-11-02-2.tar.gz"
                },
            ]

            for i, backup_data in enumerate(backups):
                started_at = datetime.utcnow() - timedelta(hours=random.randint(6, 72))
                completed_at = started_at + timedelta(minutes=random.randint(15, 120))

                backup_run = BackupRun(
                    id=i + 1,
                    backup_type=backup_data["backup_type"],
                    status=backup_data["status"],
                    started_at=started_at,
                    completed_at=completed_at,
                    size_mb=backup_data["size_mb"],
                    location=backup_data["location"]
                )
                _backup_runs.append(backup_run)
                backup_ids.append(backup_run.id)

            self.log("OPS", f"Seeded {len(backup_ids)} backup runs", backup_ids)

            # Seed 1 anomaly → suggestion workflow
            @dataclass
            class Alert:
                id: int
                severity: str
                message: str
                source: str
                created_at: datetime
                resolved: bool = False

            @dataclass
            class Suggestion:
                id: int
                suggestion_type: str
                title: str
                description: str
                priority: str
                status: str
                created_at: datetime
                alert_id: int = None

            # Create anomaly alert
            alert = Alert(
                id=1,
                severity="warning",
                message="File integrity check detected modified configuration file",
                source="file_integrity_scanner",
                created_at=datetime.utcnow() - timedelta(hours=2),
                resolved=False
            )
            _alerts.append(alert)
            self.log("OPS", "Seeded 1 anomaly alert", [alert.id])

            # Create AI suggestion based on anomaly
            suggestion = Suggestion(
                id=1,
                suggestion_type="security",
                title="Review configuration file changes",
                description="AI detected unauthorized changes to /etc/nginx/nginx.conf. "
                           "Recommend restoring from backup or validating changes.",
                priority="high",
                status="pending",
                created_at=datetime.utcnow() - timedelta(hours=1, minutes=45),
                alert_id=alert.id
            )
            _suggestions.append(suggestion)
            self.log("OPS", "Seeded 1 AI suggestion (from anomaly)", [suggestion.id])

            # Seed service health checks
            from app.models.service_health import ServiceHealth

            health_data = [
                {"service_name": "crm-api", "status": "healthy", "response_time_ms": 45.2},
                {"service_name": "ops-api", "status": "healthy", "response_time_ms": 38.1},
                {"service_name": "redis", "status": "healthy", "response_time_ms": 2.5},
                {"service_name": "postgres-crm", "status": "healthy", "response_time_ms": 12.3},
                {"service_name": "postgres-ops", "status": "healthy", "response_time_ms": 11.8},
            ]

            health_ids = []
            for i, health in enumerate(health_data):
                service_health = ServiceHealth(
                    id=i + 1,
                    service_name=health["service_name"],
                    status=health["status"],
                    last_check=datetime.utcnow() - timedelta(minutes=random.randint(1, 30)),
                    response_time_ms=health["response_time_ms"]
                )
                _service_health.append(service_health)
                health_ids.append(service_health.id)

            self.log("OPS", f"Seeded {len(health_ids)} service health checks", health_ids)

            print(f"\n✅ Ops seeding completed successfully")
            print(f"   Task runs: {len(task_ids)}")
            print(f"   Backup runs: {len(backup_ids)}")
            print(f"   Alerts: 1")
            print(f"   Suggestions: 1")
            print(f"   Service health: {len(health_ids)}")

            return True

        except Exception as e:
            print(f"❌ Ops seeding failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def print_summary(self):
        """Print seeding summary with all logged IDs."""
        print("\n" + "="*80)
        print("SEEDING SUMMARY")
        print("="*80)

        for entry in self.seed_log:
            ids_str = f" [IDs: {', '.join(map(str, entry['ids']))}]" if entry['ids'] else ""
            print(f"{entry['category']:>3} | {entry['message']}{ids_str}")

        print("="*80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Seed demo data for CRM and Ops databases"
    )

    parser.add_argument(
        "service",
        nargs="?",
        choices=["crm", "ops", "all"],
        default="all",
        help="Service to seed (default: all)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    seeder = DataSeeder(verbose=args.verbose)

    success = True

    if args.service in ["crm", "all"]:
        if not seeder.seed_crm():
            success = False

    if args.service in ["ops", "all"]:
        if not seeder.seed_ops():
            success = False

    seeder.print_summary()

    if success:
        print("\n✅ All seeding operations completed successfully")
        sys.exit(0)
    else:
        print("\n❌ Some seeding operations failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
