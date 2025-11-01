#!/usr/bin/env python3
"""
Data Retention Enforcer

Enforces retention policies by deleting or anonymizing expired records.

Features:
- Reads retention policies from configuration
- Identifies records past retention period
- Deletes or anonymizes based on policy
- Dry-run mode for safety
- Comprehensive audit logging
- Email notifications for enforcement actions

Usage:
    # Dry run (preview only)
    python scripts/data/retention_enforcer.py --dry-run

    # Enforce for specific entity
    python scripts/data/retention_enforcer.py --entity customers

    # Enforce all policies
    python scripts/data/retention_enforcer.py --all

    # Export enforcement report
    python scripts/data/retention_enforcer.py --dry-run --report enforcement_report.json

Retention policies are defined in docs/data/retention.md
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Literal
from dataclasses import dataclass, asdict
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class RetentionPolicy:
    """Retention policy for an entity"""
    entity: str  # customers, leads, audit_logs, etc.
    retention_period_days: int
    legal_basis: str
    post_retention_action: Literal["delete", "anonymize", "archive"]
    exempt_fields: List[str] = None  # Fields to keep even after anonymization


@dataclass
class EnforcementResult:
    """Result of retention enforcement"""
    entity: str
    records_identified: int
    records_deleted: int
    records_anonymized: int
    records_failed: int
    dry_run: bool
    timestamp: str
    errors: List[str] = None


# Retention policies (from docs/data/retention.md)
RETENTION_POLICIES: List[RetentionPolicy] = [
    RetentionPolicy(
        entity="customers",
        retention_period_days=7 * 365,  # 7 years
        legal_basis="Tax law (7 years), contractual obligations",
        post_retention_action="delete"
    ),
    RetentionPolicy(
        entity="leads",
        retention_period_days=2 * 365,  # 2 years
        legal_basis="Legitimate interest (GDPR Art. 6(1)(f))",
        post_retention_action="delete"
    ),
    RetentionPolicy(
        entity="invoices",
        retention_period_days=7 * 365,  # 7 years
        legal_basis="Tax law (IRS, HMRC)",
        post_retention_action="archive"
    ),
    RetentionPolicy(
        entity="audit_logs",
        retention_period_days=7 * 365,  # 7 years
        legal_basis="SOC 2, compliance requirements",
        post_retention_action="archive"
    ),
    RetentionPolicy(
        entity="marketing_consent",
        retention_period_days=3 * 365,  # 3 years
        legal_basis="GDPR Art. 6(1)(a) - consent",
        post_retention_action="delete"
    ),
    RetentionPolicy(
        entity="support_tickets",
        retention_period_days=3 * 365,  # 3 years
        legal_basis="Contractual obligation, customer service",
        post_retention_action="anonymize",
        exempt_fields=["ticket_id", "created_at", "category", "resolved_at"]
    ),
    RetentionPolicy(
        entity="sessions",
        retention_period_days=90,  # 90 days
        legal_basis="Security monitoring",
        post_retention_action="delete"
    ),
    RetentionPolicy(
        entity="application_logs",
        retention_period_days=90,  # 90 days
        legal_basis="Operational purposes",
        post_retention_action="delete"
    ),
]


class RetentionEnforcer:
    """
    Enforces retention policies on database records

    This is a stub that demonstrates the workflow.
    In production, connect to actual databases.
    """

    def __init__(self, audit_log_path: str = "logs/retention_enforcement.jsonl"):
        """
        Initialize retention enforcer

        Args:
            audit_log_path: Path to audit log
        """
        self.audit_log_path = audit_log_path
        os.makedirs(os.path.dirname(audit_log_path), exist_ok=True)

    def enforce_policy(
        self,
        policy: RetentionPolicy,
        dry_run: bool = True
    ) -> EnforcementResult:
        """
        Enforce retention policy for an entity

        Args:
            policy: Retention policy to enforce
            dry_run: If True, only preview actions without executing

        Returns:
            Enforcement result
        """
        logger.info(f"{'[DRY RUN] ' if dry_run else ''}Enforcing retention for {policy.entity}")
        logger.info(f"  Retention period: {policy.retention_period_days} days")
        logger.info(f"  Action: {policy.post_retention_action}")

        # Calculate cutoff date
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=policy.retention_period_days)
        logger.info(f"  Cutoff date: {cutoff_date.isoformat()}")

        # Identify expired records (stub - replace with actual DB queries)
        expired_records = self._identify_expired_records(policy.entity, cutoff_date)
        logger.info(f"  Found {len(expired_records)} expired records")

        if not expired_records:
            result = EnforcementResult(
                entity=policy.entity,
                records_identified=0,
                records_deleted=0,
                records_anonymized=0,
                records_failed=0,
                dry_run=dry_run,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            self._audit_log(result)
            return result

        # Execute retention action
        deleted_count = 0
        anonymized_count = 0
        failed_count = 0
        errors = []

        for record in expired_records:
            try:
                if policy.post_retention_action == "delete":
                    if not dry_run:
                        self._delete_record(policy.entity, record)
                    deleted_count += 1
                    logger.debug(f"  Deleted record: {record.get('id')}")

                elif policy.post_retention_action == "anonymize":
                    if not dry_run:
                        self._anonymize_record(policy.entity, record, policy.exempt_fields)
                    anonymized_count += 1
                    logger.debug(f"  Anonymized record: {record.get('id')}")

                elif policy.post_retention_action == "archive":
                    if not dry_run:
                        self._archive_record(policy.entity, record)
                    deleted_count += 1  # Archived = deleted from main DB
                    logger.debug(f"  Archived record: {record.get('id')}")

            except Exception as e:
                failed_count += 1
                error_msg = f"Failed to process record {record.get('id')}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"  {error_msg}")

        # Summary
        result = EnforcementResult(
            entity=policy.entity,
            records_identified=len(expired_records),
            records_deleted=deleted_count,
            records_anonymized=anonymized_count,
            records_failed=failed_count,
            dry_run=dry_run,
            timestamp=datetime.now(timezone.utc).isoformat(),
            errors=errors if errors else None
        )

        logger.info(f"  {'Would delete' if dry_run else 'Deleted'}: {deleted_count}")
        logger.info(f"  {'Would anonymize' if dry_run else 'Anonymized'}: {anonymized_count}")
        logger.info(f"  Failed: {failed_count}")

        # Audit log
        self._audit_log(result)

        return result

    def enforce_all(self, dry_run: bool = True) -> List[EnforcementResult]:
        """
        Enforce all retention policies

        Args:
            dry_run: If True, only preview actions

        Returns:
            List of enforcement results
        """
        logger.info(f"{'[DRY RUN] ' if dry_run else ''}Enforcing all retention policies")
        logger.info(f"Total policies: {len(RETENTION_POLICIES)}\n")

        results = []
        for policy in RETENTION_POLICIES:
            result = self.enforce_policy(policy, dry_run=dry_run)
            results.append(result)
            print()  # Blank line between policies

        # Summary
        total_identified = sum(r.records_identified for r in results)
        total_deleted = sum(r.records_deleted for r in results)
        total_anonymized = sum(r.records_anonymized for r in results)
        total_failed = sum(r.records_failed for r in results)

        logger.info("=== Enforcement Summary ===")
        logger.info(f"Total records identified: {total_identified}")
        logger.info(f"Total deleted: {total_deleted}")
        logger.info(f"Total anonymized: {total_anonymized}")
        logger.info(f"Total failed: {total_failed}")

        return results

    def _identify_expired_records(
        self,
        entity: str,
        cutoff_date: datetime
    ) -> List[Dict]:
        """
        Identify records past retention period

        STUB: Replace with actual database queries

        Args:
            entity: Entity type
            cutoff_date: Records before this date are expired

        Returns:
            List of expired records
        """
        # Example: In production, this would be a database query like:
        # SELECT * FROM {entity} WHERE created_at < {cutoff_date} AND deleted_at IS NULL

        # For demo, generate sample data
        sample_records = []

        if entity == "customers":
            sample_records = [
                {"id": f"cust_{i}", "created_at": (cutoff_date - timedelta(days=30 * i)).isoformat()}
                for i in range(1, 4)  # 3 sample expired customers
            ]
        elif entity == "leads":
            sample_records = [
                {"id": f"lead_{i}", "created_at": (cutoff_date - timedelta(days=10 * i)).isoformat()}
                for i in range(1, 6)  # 5 sample expired leads
            ]
        elif entity == "sessions":
            sample_records = [
                {"id": f"session_{i}", "created_at": (cutoff_date - timedelta(days=i)).isoformat()}
                for i in range(1, 11)  # 10 sample expired sessions
            ]

        return sample_records

    def _delete_record(self, entity: str, record: Dict):
        """
        Delete a record

        STUB: Replace with actual database delete

        Args:
            entity: Entity type
            record: Record to delete
        """
        # Example: In production, this would be:
        # db.execute(f"DELETE FROM {entity} WHERE id = ?", record['id'])

        logger.debug(f"DELETE FROM {entity} WHERE id = '{record['id']}'")

    def _anonymize_record(
        self,
        entity: str,
        record: Dict,
        exempt_fields: Optional[List[str]] = None
    ):
        """
        Anonymize a record (remove PII, keep metadata)

        STUB: Replace with actual database update

        Args:
            entity: Entity type
            record: Record to anonymize
            exempt_fields: Fields to keep (not anonymize)
        """
        # Example: In production, this would be:
        # UPDATE {entity} SET
        #   name = '[REDACTED]',
        #   email = '[REDACTED]',
        #   phone = '[REDACTED]',
        #   ...
        # WHERE id = record['id']

        exempt = exempt_fields or []
        logger.debug(f"ANONYMIZE {entity} WHERE id = '{record['id']}' (keep: {exempt})")

    def _archive_record(self, entity: str, record: Dict):
        """
        Archive a record (move to cold storage)

        STUB: Replace with actual archival logic

        Args:
            entity: Entity type
            record: Record to archive
        """
        # Example: In production, this would be:
        # 1. Copy record to archive table/storage
        # 2. Delete from main table

        logger.debug(f"ARCHIVE {entity} WHERE id = '{record['id']}' to cold storage")

    def _audit_log(self, result: EnforcementResult):
        """Write enforcement result to audit log"""
        with open(self.audit_log_path, 'a') as f:
            f.write(json.dumps(asdict(result)) + '\n')


def main():
    parser = argparse.ArgumentParser(description="Data Retention Enforcer")
    parser.add_argument(
        '--entity',
        type=str,
        help="Enforce retention for specific entity"
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help="Enforce all retention policies"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=True,
        help="Preview actions without executing (default: True)"
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help="Execute enforcement (disables dry-run)"
    )
    parser.add_argument(
        '--report',
        type=str,
        help="Export enforcement report to JSON file"
    )
    parser.add_argument(
        '--list-policies',
        action='store_true',
        help="List all retention policies"
    )

    args = parser.parse_args()

    # List policies
    if args.list_policies:
        print("=== Retention Policies ===\n")
        for policy in RETENTION_POLICIES:
            print(f"Entity: {policy.entity}")
            print(f"  Retention: {policy.retention_period_days} days ({policy.retention_period_days // 365} years)")
            print(f"  Legal basis: {policy.legal_basis}")
            print(f"  Action: {policy.post_retention_action}")
            if policy.exempt_fields:
                print(f"  Exempt fields: {', '.join(policy.exempt_fields)}")
            print()
        return

    # Determine dry-run mode
    dry_run = not args.execute

    # Initialize enforcer
    enforcer = RetentionEnforcer()

    # Enforce specific entity
    if args.entity:
        policy = next((p for p in RETENTION_POLICIES if p.entity == args.entity), None)
        if not policy:
            logger.error(f"No retention policy found for entity: {args.entity}")
            logger.info(f"Available entities: {', '.join(p.entity for p in RETENTION_POLICIES)}")
            sys.exit(1)

        results = [enforcer.enforce_policy(policy, dry_run=dry_run)]

    # Enforce all policies
    elif args.all or (not args.entity):
        results = enforcer.enforce_all(dry_run=dry_run)

    else:
        parser.print_help()
        sys.exit(1)

    # Export report
    if args.report:
        report_path = Path(args.report)
        report_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dry_run": dry_run,
            "results": [asdict(r) for r in results]
        }
        report_path.write_text(json.dumps(report_data, indent=2))
        logger.info(f"Exported report to: {report_path}")

    # Warning if dry-run
    if dry_run:
        print("\n⚠️  DRY RUN MODE - No changes were made")
        print("   Use --execute to actually enforce retention policies")


if __name__ == "__main__":
    main()
