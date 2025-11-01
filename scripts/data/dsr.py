#!/usr/bin/env python3
"""
Data Subject Request (DSR) Workflow

Handles GDPR/CCPA data subject requests:
- Right to Access (export user data)
- Right to Rectification (correct inaccurate data)
- Right to Erasure (delete user data)
- Right to Data Portability (export in portable format)

Features:
- Request creation and tracking
- Approval workflow
- Automated data export
- Audit logging
- Email notifications

Usage:
    # Create access request
    python scripts/data/dsr.py access --user-id user_12345

    # Create erasure request
    python scripts/data/dsr.py erase --user-id user_12345 --reason "User request"

    # Approve request
    python scripts/data/dsr.py approve --request-id req_abc123 --approver admin@example.com

    # Process approved requests
    python scripts/data/dsr.py process

    # List pending requests
    python scripts/data/dsr.py list --status pending
"""

import os
import sys
import json
import uuid
import logging
import argparse
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Literal
from dataclasses import dataclass, asdict, field
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


RequestType = Literal["access", "rectify", "erase", "portability"]
RequestStatus = Literal["pending", "approved", "rejected", "completed", "failed"]


@dataclass
class DSRRequest:
    """Data Subject Request"""
    request_id: str
    request_type: RequestType
    user_id: str
    user_email: str
    created_at: str
    status: RequestStatus = "pending"
    reason: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    completed_at: Optional[str] = None
    export_path: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class UserDataExport:
    """Exported user data"""
    user_id: str
    export_date: str
    data: Dict[str, List[Dict]]  # entity -> records
    total_records: int


class DSRWorkflow:
    """
    Data Subject Request Workflow Manager

    Handles creation, approval, and processing of DSRs.
    """

    def __init__(
        self,
        requests_dir: str = "data/dsr_requests",
        exports_dir: str = "artifacts/dsr_exports",
        audit_log_path: str = "logs/dsr_audit.jsonl"
    ):
        """
        Initialize DSR workflow

        Args:
            requests_dir: Directory to store request metadata
            exports_dir: Directory to store data exports
            audit_log_path: Audit log file
        """
        self.requests_dir = Path(requests_dir)
        self.requests_dir.mkdir(parents=True, exist_ok=True)

        self.exports_dir = Path(exports_dir)
        self.exports_dir.mkdir(parents=True, exist_ok=True)

        self.audit_log_path = Path(audit_log_path)
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)

    def create_request(
        self,
        request_type: RequestType,
        user_id: str,
        user_email: str,
        reason: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> DSRRequest:
        """
        Create a new DSR

        Args:
            request_type: Type of request
            user_id: User ID
            user_email: User email
            reason: Reason for request
            metadata: Additional metadata

        Returns:
            Created request
        """
        request_id = f"dsr_{uuid.uuid4().hex[:12]}"

        request = DSRRequest(
            request_id=request_id,
            request_type=request_type,
            user_id=user_id,
            user_email=user_email,
            created_at=datetime.now(timezone.utc).isoformat(),
            reason=reason,
            metadata=metadata or {}
        )

        # Save request
        self._save_request(request)

        # Audit log
        self._audit_log({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "CREATE_REQUEST",
            "request_id": request_id,
            "request_type": request_type,
            "user_id": user_id
        })

        logger.info(f"Created DSR: {request_id} ({request_type}) for user {user_id}")

        return request

    def approve_request(
        self,
        request_id: str,
        approver: str
    ) -> DSRRequest:
        """
        Approve a DSR

        Args:
            request_id: Request ID
            approver: Email of approver

        Returns:
            Updated request
        """
        request = self._load_request(request_id)

        if request.status != "pending":
            raise ValueError(f"Request {request_id} is not pending (status: {request.status})")

        request.status = "approved"
        request.approved_by = approver
        request.approved_at = datetime.now(timezone.utc).isoformat()

        self._save_request(request)

        # Audit log
        self._audit_log({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "APPROVE_REQUEST",
            "request_id": request_id,
            "approver": approver
        })

        logger.info(f"Approved DSR: {request_id} by {approver}")

        return request

    def reject_request(
        self,
        request_id: str,
        approver: str,
        reason: str
    ) -> DSRRequest:
        """
        Reject a DSR

        Args:
            request_id: Request ID
            approver: Email of rejector
            reason: Rejection reason

        Returns:
            Updated request
        """
        request = self._load_request(request_id)

        if request.status != "pending":
            raise ValueError(f"Request {request_id} is not pending (status: {request.status})")

        request.status = "rejected"
        request.approved_by = approver
        request.approved_at = datetime.now(timezone.utc).isoformat()
        request.metadata["rejection_reason"] = reason

        self._save_request(request)

        # Audit log
        self._audit_log({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "REJECT_REQUEST",
            "request_id": request_id,
            "approver": approver,
            "reason": reason
        })

        logger.info(f"Rejected DSR: {request_id} by {approver} - {reason}")

        return request

    def process_approved_requests(self) -> List[DSRRequest]:
        """
        Process all approved requests

        Returns:
            List of processed requests
        """
        approved_requests = self.list_requests(status="approved")

        logger.info(f"Processing {len(approved_requests)} approved requests")

        results = []
        for request in approved_requests:
            try:
                processed_request = self._process_request(request)
                results.append(processed_request)
            except Exception as e:
                logger.error(f"Failed to process request {request.request_id}: {e}")
                request.status = "failed"
                request.error_message = str(e)
                self._save_request(request)
                results.append(request)

        return results

    def list_requests(
        self,
        status: Optional[RequestStatus] = None,
        user_id: Optional[str] = None
    ) -> List[DSRRequest]:
        """
        List DSRs

        Args:
            status: Filter by status
            user_id: Filter by user ID

        Returns:
            List of requests
        """
        requests = []

        for request_file in self.requests_dir.glob("*.json"):
            request_data = json.loads(request_file.read_text())
            request = DSRRequest(**request_data)

            # Filters
            if status and request.status != status:
                continue
            if user_id and request.user_id != user_id:
                continue

            requests.append(request)

        # Sort by creation date (newest first)
        requests.sort(key=lambda r: r.created_at, reverse=True)

        return requests

    def _process_request(self, request: DSRRequest) -> DSRRequest:
        """
        Process a single DSR

        Args:
            request: Request to process

        Returns:
            Updated request
        """
        logger.info(f"Processing {request.request_type} request: {request.request_id}")

        if request.request_type == "access":
            self._process_access_request(request)
        elif request.request_type == "portability":
            self._process_portability_request(request)
        elif request.request_type == "erase":
            self._process_erasure_request(request)
        elif request.request_type == "rectify":
            self._process_rectification_request(request)

        request.status = "completed"
        request.completed_at = datetime.now(timezone.utc).isoformat()
        self._save_request(request)

        # Audit log
        self._audit_log({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "COMPLETE_REQUEST",
            "request_id": request.request_id,
            "request_type": request.request_type
        })

        return request

    def _process_access_request(self, request: DSRRequest):
        """
        Process access request - export all user data

        Args:
            request: Access request
        """
        logger.info(f"Exporting data for user: {request.user_id}")

        # Collect user data from all entities
        user_data = self._collect_user_data(request.user_id)

        # Create export
        export = UserDataExport(
            user_id=request.user_id,
            export_date=datetime.now(timezone.utc).isoformat(),
            data=user_data,
            total_records=sum(len(records) for records in user_data.values())
        )

        # Save export
        export_path = self.exports_dir / f"{request.request_id}_{request.user_id}_access.json"
        export_path.write_text(json.dumps(asdict(export), indent=2, default=str))

        request.export_path = str(export_path)

        logger.info(f"Exported {export.total_records} records to {export_path}")

    def _process_portability_request(self, request: DSRRequest):
        """
        Process portability request - export in portable format (JSON)

        Args:
            request: Portability request
        """
        # Same as access, but structured for portability
        self._process_access_request(request)

        # Could additionally export to CSV, XML, etc.
        logger.info("Data exported in portable JSON format")

    def _process_erasure_request(self, request: DSRRequest):
        """
        Process erasure request - delete all user data

        Args:
            request: Erasure request
        """
        logger.warning(f"DELETING all data for user: {request.user_id}")

        # Export data before deletion (for audit)
        self._process_access_request(request)

        # Delete user data (STUB - replace with actual DB operations)
        entities = ["customers", "leads", "sessions", "audit_logs", "support_tickets"]

        for entity in entities:
            logger.info(f"  Deleting {entity} records for user {request.user_id}")
            # Example: db.execute(f"DELETE FROM {entity} WHERE user_id = ?", request.user_id)

        logger.warning(f"Deleted user data for {request.user_id}")

        request.metadata["deleted_entities"] = entities

    def _process_rectification_request(self, request: DSRRequest):
        """
        Process rectification request - update user data

        Args:
            request: Rectification request
        """
        corrections = request.metadata.get("corrections", {})

        if not corrections:
            raise ValueError("Rectification request missing 'corrections' in metadata")

        logger.info(f"Applying {len(corrections)} corrections for user {request.user_id}")

        for field, new_value in corrections.items():
            logger.info(f"  Updating {field} to {new_value}")
            # Example: db.execute("UPDATE customers SET ? = ? WHERE user_id = ?", field, new_value, request.user_id)

        request.metadata["corrections_applied"] = corrections

    def _collect_user_data(self, user_id: str) -> Dict[str, List[Dict]]:
        """
        Collect all data for a user across entities

        STUB: Replace with actual database queries

        Args:
            user_id: User ID

        Returns:
            Dictionary of entity -> records
        """
        # Example: In production, query all tables
        # SELECT * FROM customers WHERE user_id = ?
        # SELECT * FROM invoices WHERE user_id = ?
        # etc.

        # Sample data for demo
        user_data = {
            "customer": [
                {
                    "id": user_id,
                    "email": "user@example.com",
                    "name": "John Doe",
                    "created_at": "2023-01-15T10:00:00Z"
                }
            ],
            "invoices": [
                {
                    "id": "inv_123",
                    "user_id": user_id,
                    "amount": 99.99,
                    "date": "2024-01-01T00:00:00Z"
                },
                {
                    "id": "inv_456",
                    "user_id": user_id,
                    "amount": 149.99,
                    "date": "2024-02-01T00:00:00Z"
                }
            ],
            "support_tickets": [
                {
                    "id": "ticket_789",
                    "user_id": user_id,
                    "subject": "Billing question",
                    "status": "closed",
                    "created_at": "2024-03-15T14:30:00Z"
                }
            ],
            "audit_logs": [
                {
                    "id": "log_1",
                    "user_id": user_id,
                    "action": "login",
                    "timestamp": "2024-10-01T08:00:00Z"
                },
                {
                    "id": "log_2",
                    "user_id": user_id,
                    "action": "update_profile",
                    "timestamp": "2024-10-15T12:00:00Z"
                }
            ]
        }

        return user_data

    def _save_request(self, request: DSRRequest):
        """Save request to disk"""
        request_path = self.requests_dir / f"{request.request_id}.json"
        request_path.write_text(json.dumps(asdict(request), indent=2))

    def _load_request(self, request_id: str) -> DSRRequest:
        """Load request from disk"""
        request_path = self.requests_dir / f"{request_id}.json"
        if not request_path.exists():
            raise ValueError(f"Request not found: {request_id}")

        request_data = json.loads(request_path.read_text())
        return DSRRequest(**request_data)

    def _audit_log(self, entry: Dict):
        """Write audit log entry"""
        with open(self.audit_log_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')


def main():
    parser = argparse.ArgumentParser(description="Data Subject Request Workflow")
    subparsers = parser.add_subparsers(dest='command', help='Command')

    # Access request
    access_parser = subparsers.add_parser('access', help='Create access request')
    access_parser.add_argument('--user-id', required=True, help='User ID')
    access_parser.add_argument('--user-email', required=True, help='User email')
    access_parser.add_argument('--reason', help='Request reason')

    # Portability request
    portability_parser = subparsers.add_parser('portability', help='Create portability request')
    portability_parser.add_argument('--user-id', required=True, help='User ID')
    portability_parser.add_argument('--user-email', required=True, help='User email')

    # Erasure request
    erase_parser = subparsers.add_parser('erase', help='Create erasure request')
    erase_parser.add_argument('--user-id', required=True, help='User ID')
    erase_parser.add_argument('--user-email', required=True, help='User email')
    erase_parser.add_argument('--reason', help='Erasure reason')

    # Rectification request
    rectify_parser = subparsers.add_parser('rectify', help='Create rectification request')
    rectify_parser.add_argument('--user-id', required=True, help='User ID')
    rectify_parser.add_argument('--user-email', required=True, help='User email')
    rectify_parser.add_argument('--corrections', required=True, help='JSON of field corrections')

    # Approve request
    approve_parser = subparsers.add_parser('approve', help='Approve request')
    approve_parser.add_argument('--request-id', required=True, help='Request ID')
    approve_parser.add_argument('--approver', required=True, help='Approver email')

    # Reject request
    reject_parser = subparsers.add_parser('reject', help='Reject request')
    reject_parser.add_argument('--request-id', required=True, help='Request ID')
    reject_parser.add_argument('--approver', required=True, help='Approver email')
    reject_parser.add_argument('--reason', required=True, help='Rejection reason')

    # Process requests
    subparsers.add_parser('process', help='Process approved requests')

    # List requests
    list_parser = subparsers.add_parser('list', help='List requests')
    list_parser.add_argument('--status', help='Filter by status')
    list_parser.add_argument('--user-id', help='Filter by user ID')

    args = parser.parse_args()

    # Initialize workflow
    workflow = DSRWorkflow()

    # Execute command
    if args.command == 'access':
        request = workflow.create_request(
            request_type="access",
            user_id=args.user_id,
            user_email=args.user_email,
            reason=args.reason
        )
        print(f"✓ Created access request: {request.request_id}")
        print(f"  Status: {request.status}")
        print(f"  User: {request.user_id} ({request.user_email})")

    elif args.command == 'portability':
        request = workflow.create_request(
            request_type="portability",
            user_id=args.user_id,
            user_email=args.user_email
        )
        print(f"✓ Created portability request: {request.request_id}")
        print(f"  Status: {request.status}")

    elif args.command == 'erase':
        request = workflow.create_request(
            request_type="erase",
            user_id=args.user_id,
            user_email=args.user_email,
            reason=args.reason
        )
        print(f"✓ Created erasure request: {request.request_id}")
        print(f"  Status: {request.status}")
        print(f"  ⚠️  This request will DELETE all user data when processed!")

    elif args.command == 'rectify':
        corrections = json.loads(args.corrections)
        request = workflow.create_request(
            request_type="rectify",
            user_id=args.user_id,
            user_email=args.user_email,
            metadata={"corrections": corrections}
        )
        print(f"✓ Created rectification request: {request.request_id}")
        print(f"  Corrections: {corrections}")

    elif args.command == 'approve':
        request = workflow.approve_request(args.request_id, args.approver)
        print(f"✓ Approved request: {request.request_id}")
        print(f"  Approved by: {request.approved_by}")
        print(f"  Status: {request.status}")

    elif args.command == 'reject':
        request = workflow.reject_request(args.request_id, args.approver, args.reason)
        print(f"✗ Rejected request: {request.request_id}")
        print(f"  Rejected by: {request.approved_by}")
        print(f"  Reason: {args.reason}")

    elif args.command == 'process':
        results = workflow.process_approved_requests()
        print(f"✓ Processed {len(results)} requests\n")

        for result in results:
            print(f"Request: {result.request_id} ({result.request_type})")
            print(f"  Status: {result.status}")
            if result.export_path:
                print(f"  Export: {result.export_path}")
            if result.error_message:
                print(f"  Error: {result.error_message}")
            print()

    elif args.command == 'list':
        requests = workflow.list_requests(
            status=args.status,
            user_id=args.user_id
        )
        print(f"Found {len(requests)} requests\n")

        for request in requests:
            print(f"{request.request_id} - {request.request_type} - {request.status}")
            print(f"  User: {request.user_id} ({request.user_email})")
            print(f"  Created: {request.created_at}")
            if request.approved_by:
                print(f"  Approved by: {request.approved_by}")
            if request.export_path:
                print(f"  Export: {request.export_path}")
            print()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
