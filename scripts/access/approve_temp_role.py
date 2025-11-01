#!/usr/bin/env python3
"""
Break-Glass Temporary Role Approval System

This script manages temporary privilege elevation with dual approval requirements.

Features:
- Dual approval enforcement (minimum 2 approvers)
- Time-limited access (automatic expiration)
- Immutable audit logging
- Token generation with break-glass claims
- Self-approval prevention
- Approval timeout (30 minutes)

Usage:
    # Request break-glass access
    python scripts/access/approve_temp_role.py request \\
        --user devops@example.com \\
        --reason "Critical production incident" \\
        --duration 4

    # Approve request
    python scripts/access/approve_temp_role.py approve \\
        --request-id bg-2024-001 \\
        --approver manager@example.com

    # Check status
    python scripts/access/approve_temp_role.py status \\
        --request-id bg-2024-001

    # Revoke access
    python scripts/access/approve_temp_role.py revoke \\
        --request-id bg-2024-001 \\
        --revoker security@example.com \\
        --reason "Incident resolved"

    # Generate audit report
    python scripts/access/approve_temp_role.py report \\
        --start-date 2024-01-01 \\
        --end-date 2024-12-31
"""

import argparse
import json
import time
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import secrets
import hashlib
import hmac
import base64


# Configuration
APPROVALS_REQUIRED = 2
APPROVAL_TIMEOUT_MINUTES = 30
DEFAULT_DURATION_HOURS = 4
MAX_DURATION_HOURS = 24

# File paths
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent
REQUESTS_DIR = REPO_ROOT / "secrets" / "break_glass_requests"
AUDIT_LOG = REPO_ROOT / "secrets" / "break_glass_audit.log"

# Ensure directories exist
REQUESTS_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)


class BreakGlassRequest:
    """Represents a break-glass access request"""

    def __init__(
        self,
        request_id: str,
        user: str,
        reason: str,
        duration_hours: int,
        created_at: float = None
    ):
        self.request_id = request_id
        self.user = user
        self.reason = reason
        self.duration_hours = duration_hours
        self.created_at = created_at or time.time()
        self.approvals: List[Dict[str, any]] = []
        self.status = "pending"
        self.granted_at: Optional[float] = None
        self.expires_at: Optional[float] = None
        self.revoked_at: Optional[float] = None
        self.revoked_by: Optional[str] = None
        self.revoke_reason: Optional[str] = None
        self.token: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "request_id": self.request_id,
            "user": self.user,
            "reason": self.reason,
            "duration_hours": self.duration_hours,
            "created_at": self.created_at,
            "approvals": self.approvals,
            "status": self.status,
            "granted_at": self.granted_at,
            "expires_at": self.expires_at,
            "revoked_at": self.revoked_at,
            "revoked_by": self.revoked_by,
            "revoke_reason": self.revoke_reason,
            "token": self.token
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "BreakGlassRequest":
        req = cls(
            request_id=data["request_id"],
            user=data["user"],
            reason=data["reason"],
            duration_hours=data["duration_hours"],
            created_at=data["created_at"]
        )
        req.approvals = data.get("approvals", [])
        req.status = data.get("status", "pending")
        req.granted_at = data.get("granted_at")
        req.expires_at = data.get("expires_at")
        req.revoked_at = data.get("revoked_at")
        req.revoked_by = data.get("revoked_by")
        req.revoke_reason = data.get("revoke_reason")
        req.token = data.get("token")
        return req

    def save(self):
        """Save request to disk"""
        filepath = REQUESTS_DIR / f"{self.request_id}.json"
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, request_id: str) -> Optional["BreakGlassRequest"]:
        """Load request from disk"""
        filepath = REQUESTS_DIR / f"{request_id}.json"
        if not filepath.exists():
            return None

        with open(filepath, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def add_approval(self, approver: str) -> bool:
        """
        Add an approval

        Returns:
            True if approval added, False if invalid
        """
        # Check self-approval
        if approver == self.user:
            print(f"❌ Self-approval not allowed: {approver} cannot approve their own request")
            return False

        # Check duplicate approval
        existing_approvers = [a["approver"] for a in self.approvals]
        if approver in existing_approvers:
            print(f"❌ Duplicate approval: {approver} has already approved this request")
            return False

        # Check request age (approval timeout)
        age_minutes = (time.time() - self.created_at) / 60
        if age_minutes > APPROVAL_TIMEOUT_MINUTES:
            print(f"❌ Request expired: created {age_minutes:.1f} minutes ago (timeout: {APPROVAL_TIMEOUT_MINUTES} min)")
            return False

        # Add approval
        approval = {
            "approver": approver,
            "approved_at": time.time(),
            "approved_at_iso": datetime.utcnow().isoformat() + "Z"
        }
        self.approvals.append(approval)

        # Log approval
        log_audit_event({
            "event_type": "break_glass_approval",
            "request_id": self.request_id,
            "approver": approver,
            "approval_number": len(self.approvals)
        })

        # Check if we have enough approvals
        if len(self.approvals) >= APPROVALS_REQUIRED:
            self._grant_access()

        self.save()
        return True

    def _grant_access(self):
        """Grant break-glass access after sufficient approvals"""
        self.status = "granted"
        self.granted_at = time.time()
        self.expires_at = self.granted_at + (self.duration_hours * 3600)

        # Generate break-glass token
        self.token = self._generate_token()

        # Log grant event
        log_audit_event({
            "event_type": "break_glass_granted",
            "request_id": self.request_id,
            "user": self.user,
            "approvers": [a["approver"] for a in self.approvals],
            "granted_at": self.granted_at,
            "expires_at": self.expires_at,
            "duration_hours": self.duration_hours
        })

        self.save()

    def _generate_token(self) -> str:
        """Generate JWT token with break-glass claims"""
        # In production, use proper JWT library
        # For stub, we create a simple token structure

        now = int(time.time())
        claims = {
            "sub": self.user,
            "roles": ["OWNER"],  # Grant OWNER role temporarily
            "break_glass_approved": True,
            "break_glass_approvers": [a["approver"] for a in self.approvals],
            "break_glass_request_id": self.request_id,
            "break_glass_reason": self.reason,
            "break_glass_expires_at": int(self.expires_at),
            "exp": int(self.expires_at),
            "iat": now,
            "iss": "break-glass-system"
        }

        # Create JWT (stub implementation)
        header = {"alg": "HS256", "typ": "JWT"}
        header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
        claims_b64 = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=")

        # Sign with secret (in production, use proper key management)
        secret = os.environ.get("JWT_SECRET", "break-glass-secret-key")
        message = f"{header_b64}.{claims_b64}"
        signature = hmac.new(secret.encode(), message.encode(), hashlib.sha256).digest()
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")

        return f"{message}.{signature_b64}"

    def revoke(self, revoker: str, reason: str):
        """Revoke break-glass access"""
        self.status = "revoked"
        self.revoked_at = time.time()
        self.revoked_by = revoker
        self.revoke_reason = reason

        # Log revocation
        log_audit_event({
            "event_type": "break_glass_revoked",
            "request_id": self.request_id,
            "user": self.user,
            "revoked_by": revoker,
            "reason": reason
        })

        self.save()

    def is_active(self) -> bool:
        """Check if break-glass access is currently active"""
        if self.status != "granted":
            return False

        if self.revoked_at:
            return False

        # Check expiration
        now = time.time()
        return now < self.expires_at


def log_audit_event(event: Dict):
    """Log event to immutable audit log"""
    event["timestamp"] = time.time()
    event["timestamp_iso"] = datetime.utcnow().isoformat() + "Z"

    with open(AUDIT_LOG, "a") as f:
        f.write(json.dumps(event) + "\n")


def generate_request_id() -> str:
    """Generate unique request ID"""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    random_suffix = secrets.token_hex(4)
    return f"bg-{today}-{random_suffix}"


def cmd_request(args):
    """Create a new break-glass request"""
    # Validate duration
    if args.duration > MAX_DURATION_HOURS:
        print(f"❌ Duration too long: {args.duration}h (max: {MAX_DURATION_HOURS}h)")
        return 1

    # Generate request ID
    request_id = generate_request_id()

    # Create request
    request = BreakGlassRequest(
        request_id=request_id,
        user=args.user,
        reason=args.reason,
        duration_hours=args.duration
    )
    request.save()

    # Log request creation
    log_audit_event({
        "event_type": "break_glass_request",
        "request_id": request_id,
        "requester": args.user,
        "reason": args.reason,
        "duration_hours": args.duration
    })

    # Print summary
    print("\n" + "="*60)
    print("Break-Glass Request Created")
    print("="*60)
    print(f"Request ID: {request_id}")
    print(f"User: {args.user}")
    print(f"Reason: {args.reason}")
    print(f"Duration: {args.duration} hours")
    print(f"Status: PENDING_APPROVAL")
    print(f"Approvers Needed: {APPROVALS_REQUIRED}")
    print(f"\nWaiting for approvals...")
    print("\nApprovers can approve with:")
    print(f"  python scripts/access/approve_temp_role.py approve \\")
    print(f"      --request-id {request_id} \\")
    print(f"      --approver <approver-email>")
    print()

    return 0


def cmd_approve(args):
    """Approve a break-glass request"""
    # Load request
    request = BreakGlassRequest.load(args.request_id)
    if not request:
        print(f"❌ Request not found: {args.request_id}")
        return 1

    # Check if already granted or revoked
    if request.status == "granted":
        print(f"✅ Request already granted")
        print_request_status(request)
        return 0

    if request.status == "revoked":
        print(f"❌ Request was revoked")
        return 1

    # Add approval
    if not request.add_approval(args.approver):
        return 1

    # Check status
    if request.status == "granted":
        print("\n" + "="*60)
        print("✅ Break-Glass Access APPROVED")
        print("="*60)
        print_request_status(request)
        print("\n⚠️  IMPORTANT: This token grants OWNER-level access across all systems.")
        print("              Use responsibly and only for the stated reason.")
        print("              All actions will be audited.")
        print()
    else:
        approvals_remaining = APPROVALS_REQUIRED - len(request.approvals)
        print("\n" + "="*60)
        print(f"Approval {len(request.approvals)}/{APPROVALS_REQUIRED} Recorded")
        print("="*60)
        print(f"Approver: {args.approver}")
        print(f"Approved At: {datetime.utcnow().isoformat()}Z")
        print(f"\nWaiting for {approvals_remaining} more approval(s)...")
        print()

    return 0


def cmd_status(args):
    """Check status of a break-glass request"""
    request = BreakGlassRequest.load(args.request_id)
    if not request:
        print(f"❌ Request not found: {args.request_id}")
        return 1

    print("\n" + "="*60)
    print("Break-Glass Request Status")
    print("="*60)
    print_request_status(request)
    print()

    return 0


def cmd_revoke(args):
    """Revoke break-glass access"""
    request = BreakGlassRequest.load(args.request_id)
    if not request:
        print(f"❌ Request not found: {args.request_id}")
        return 1

    if request.status != "granted":
        print(f"❌ Request is not active (status: {request.status})")
        return 1

    request.revoke(args.revoker, args.reason)

    print("\n" + "="*60)
    print("✅ Break-Glass Access REVOKED")
    print("="*60)
    print(f"Request ID: {request.request_id}")
    print(f"User: {request.user}")
    print(f"Revoked By: {args.revoker}")
    print(f"Reason: {args.reason}")
    print(f"Revoked At: {datetime.utcnow().isoformat()}Z")
    print()

    return 0


def cmd_report(args):
    """Generate audit report"""
    print("\n" + "="*60)
    print(f"Break-Glass Audit Report")
    print(f"Period: {args.start_date} to {args.end_date}")
    print("="*60)
    print()

    # Read audit log
    if not AUDIT_LOG.exists():
        print("No audit events found")
        return 0

    events = []
    with open(AUDIT_LOG, "r") as f:
        for line in f:
            try:
                event = json.loads(line.strip())
                events.append(event)
            except:
                continue

    # Filter by date range
    start_ts = datetime.fromisoformat(args.start_date).timestamp()
    end_ts = datetime.fromisoformat(args.end_date).timestamp() + 86400  # Include end date

    filtered_events = [e for e in events if start_ts <= e["timestamp"] < end_ts]

    # Summarize
    requests_created = len([e for e in filtered_events if e["event_type"] == "break_glass_request"])
    requests_granted = len([e for e in filtered_events if e["event_type"] == "break_glass_granted"])
    requests_revoked = len([e for e in filtered_events if e["event_type"] == "break_glass_revoked"])

    print(f"Total Requests: {requests_created}")
    print(f"Granted: {requests_granted}")
    print(f"Revoked: {requests_revoked}")
    print()

    # List all requests in period
    request_events = [e for e in filtered_events if e["event_type"] == "break_glass_request"]
    if request_events:
        print("Requests:")
        for event in request_events:
            print(f"  - {event['request_id']}: {event['requester']} - {event['reason'][:50]}")

    print()
    print(f"Full audit log: {AUDIT_LOG}")
    print()

    return 0


def print_request_status(request: BreakGlassRequest):
    """Print formatted request status"""
    print(f"Request ID: {request.request_id}")
    print(f"User: {request.user}")
    print(f"Reason: {request.reason}")
    print(f"Duration: {request.duration_hours} hours")
    print(f"Status: {request.status.upper()}")
    print(f"Created: {datetime.fromtimestamp(request.created_at).isoformat()}Z")

    if request.approvals:
        print(f"\nApprovals ({len(request.approvals)}/{APPROVALS_REQUIRED}):")
        for i, approval in enumerate(request.approvals, 1):
            print(f"  {i}. {approval['approver']} at {approval['approved_at_iso']}")

    if request.granted_at:
        print(f"\nGranted At: {datetime.fromtimestamp(request.granted_at).isoformat()}Z")
        print(f"Expires At: {datetime.fromtimestamp(request.expires_at).isoformat()}Z")

        # Check if still active
        if request.is_active():
            remaining_hours = (request.expires_at - time.time()) / 3600
            print(f"Time Remaining: {remaining_hours:.1f} hours")
            print(f"\nTemporary Token:")
            print(f"{request.token[:50]}...")
        else:
            print(f"Status: EXPIRED")

    if request.revoked_at:
        print(f"\nRevoked At: {datetime.fromtimestamp(request.revoked_at).isoformat()}Z")
        print(f"Revoked By: {request.revoked_by}")
        print(f"Revoke Reason: {request.revoke_reason}")


def main():
    parser = argparse.ArgumentParser(
        description="Break-Glass Temporary Role Approval System"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Request command
    request_parser = subparsers.add_parser("request", help="Create break-glass request")
    request_parser.add_argument("--user", required=True, help="User requesting access")
    request_parser.add_argument("--reason", required=True, help="Reason for break-glass access")
    request_parser.add_argument("--duration", type=int, default=DEFAULT_DURATION_HOURS,
                                help=f"Duration in hours (default: {DEFAULT_DURATION_HOURS}, max: {MAX_DURATION_HOURS})")

    # Approve command
    approve_parser = subparsers.add_parser("approve", help="Approve break-glass request")
    approve_parser.add_argument("--request-id", required=True, help="Request ID to approve")
    approve_parser.add_argument("--approver", required=True, help="Email of approver")

    # Status command
    status_parser = subparsers.add_parser("status", help="Check request status")
    status_parser.add_argument("--request-id", required=True, help="Request ID to check")

    # Revoke command
    revoke_parser = subparsers.add_parser("revoke", help="Revoke break-glass access")
    revoke_parser.add_argument("--request-id", required=True, help="Request ID to revoke")
    revoke_parser.add_argument("--revoker", required=True, help="Email of person revoking access")
    revoke_parser.add_argument("--reason", required=True, help="Reason for revocation")

    # Report command
    report_parser = subparsers.add_parser("report", help="Generate audit report")
    report_parser.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    report_parser.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    if args.command == "request":
        return cmd_request(args)
    elif args.command == "approve":
        return cmd_approve(args)
    elif args.command == "status":
        return cmd_status(args)
    elif args.command == "revoke":
        return cmd_revoke(args)
    elif args.command == "report":
        return cmd_report(args)


if __name__ == "__main__":
    sys.exit(main())
