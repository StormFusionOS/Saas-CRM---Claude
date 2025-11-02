"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Email poller service.

For testing: polls a local filesystem "inbox" directory for mock email files.
In production: connect to IMAP/POP3 or email service API.
"""

import os
import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import structlog

from app.db import InMemoryDB
from app.services.intake import ingest_lead_from_webhook


logger = structlog.get_logger(__name__)


class EmailPoller:
    """
    Poll for incoming emails and convert them to leads.

    For testing purposes, this reads JSON files from a local inbox directory.
    """

    def __init__(self, inbox_dir: str = "/tmp/crm_inbox"):
        self.inbox_dir = Path(inbox_dir)
        self.processed_dir = self.inbox_dir / "processed"

        # Ensure directories exist
        self.inbox_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def poll(self, db: InMemoryDB) -> List[Dict]:
        """
        Poll inbox for new emails.

        Args:
            db: Database session

        Returns:
            List of processed email results
        """
        results = []

        # Find all .json files in inbox
        for email_file in self.inbox_dir.glob("*.json"):
            try:
                result = self._process_email_file(db, email_file)
                results.append(result)
            except Exception as e:
                logger.error(
                    "failed_to_process_email",
                    file=str(email_file),
                    error=str(e)
                )
                results.append({
                    "file": str(email_file),
                    "status": "error",
                    "error": str(e)
                })

        return results

    def _process_email_file(self, db: InMemoryDB, email_file: Path) -> Dict:
        """
        Process a single email file.

        Expected JSON format:
        {
            "from": "customer@example.com",
            "subject": "Inquiry about services",
            "body": "I'm interested in your services...",
            "date": "2024-01-01T12:00:00Z",
            "metadata": { ... }
        }
        """
        logger.info("processing_email_file", file=str(email_file))

        # Read email data
        with open(email_file, 'r') as f:
            email_data = json.load(f)

        # Extract email address and parse name
        from_email = email_data.get('from', '')
        from_parts = from_email.split('<')

        email = None
        name_parts = None

        if len(from_parts) == 2:
            # Format: "John Doe <john@example.com>"
            name = from_parts[0].strip()
            email = from_parts[1].strip('> ')
            name_parts = name.split(' ', 1)
        else:
            # Format: "john@example.com"
            email = from_email.strip()

        # Parse name
        first_name = None
        last_name = None
        if name_parts:
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else None

        # Prepare lead data
        lead_data = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'subject': email_data.get('subject', 'No subject'),
            'body': email_data.get('body', ''),
            'interaction_type': 'EMAIL',
            'custom_fields': email_data.get('metadata', {}),
        }

        # Ingest lead
        result = ingest_lead_from_webhook(
            db=db,
            source="EMAIL",
            lead_data=lead_data
        )

        # Move file to processed
        processed_file = self.processed_dir / email_file.name
        email_file.rename(processed_file)

        logger.info(
            "email_processed",
            file=str(email_file),
            contact_id=result['contact_id'],
            lead_id=result['lead_id']
        )

        return {
            "file": str(email_file),
            "status": "success",
            **result
        }


def create_sample_inbox(inbox_dir: str = "/tmp/crm_inbox"):
    """
    Create sample email files for testing.

    Args:
        inbox_dir: Inbox directory path
    """
    inbox_path = Path(inbox_dir)
    inbox_path.mkdir(parents=True, exist_ok=True)

    # Sample emails
    samples = [
        {
            "from": "John Smith <john.smith@example.com>",
            "subject": "Interested in your CRM solution",
            "body": "Hi, I'm looking for a CRM solution for my small business. Can you provide more information?",
            "date": datetime.utcnow().isoformat(),
            "metadata": {
                "source": "website_contact_form"
            }
        },
        {
            "from": "sarah.jones@techcorp.com",
            "subject": "Demo request",
            "body": "We're interested in scheduling a demo of your platform.",
            "date": datetime.utcnow().isoformat(),
            "metadata": {
                "company": "TechCorp Inc."
            }
        }
    ]

    for i, email_data in enumerate(samples, 1):
        file_path = inbox_path / f"email_{i}.json"
        with open(file_path, 'w') as f:
            json.dump(email_data, f, indent=2)

    logger.info("created_sample_emails", count=len(samples), inbox=str(inbox_path))


__all__ = ["EmailPoller", "create_sample_inbox"]
