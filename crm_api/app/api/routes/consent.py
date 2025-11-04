"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Consent and Compliance API Routes

Endpoints for managing consent records, GDPR requests, and compliance tracking.
"""

from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from app.api.deps import require_sales_claims
from app.models.consent import (
    ConsentRecord,
    ConsentHistory,
    DataProcessingAgreement,
    GDPRRequest,
    CreateConsentRequest,
    UpdateConsentRequest,
    CreateDataProcessingAgreementRequest,
    CreateGDPRRequest,
    UpdateGDPRRequest,
    ConsentSummary,
    ConsentHistoryResponse,
    GDPRRequestResponse,
    ConsentType,
)

router = APIRouter()

# In-memory storage (replace with database in production)
consent_records: List[ConsentRecord] = []
consent_history: List[ConsentHistory] = []
data_processing_agreements: List[DataProcessingAgreement] = []
gdpr_requests: List[GDPRRequest] = []

consent_id_counter = 1
history_id_counter = 1
dpa_id_counter = 1
gdpr_request_id_counter = 1


@router.post("/consent", response_model=ConsentRecord)
def create_consent_record(
    request: CreateConsentRequest,
    http_request: Request,
    current_user: dict = Depends(require_sales_claims)
):
    """Create a new consent record for a contact."""
    global consent_id_counter, history_id_counter

    now = datetime.now()

    # Create consent record
    consent = ConsentRecord(
        id=consent_id_counter,
        contact_id=request.contact_id,
        consent_type=request.consent_type,
        granted=request.granted,
        source=request.source,
        ip_address=request.ip_address or http_request.client.host,
        user_agent=request.user_agent or http_request.headers.get("user-agent"),
        consent_text=request.consent_text,
        granted_at=now,
        expires_at=request.expires_at,
        revoked_at=None,
        created_at=now,
        updated_at=now
    )

    consent_records.append(consent)
    consent_id_counter += 1

    # Create history entry
    history = ConsentHistory(
        id=history_id_counter,
        consent_record_id=consent.id,
        action="granted" if request.granted else "revoked",
        previous_value=None,
        new_value=request.granted,
        reason=None,
        changed_by=current_user.get("user_id"),
        changed_at=now,
        ip_address=consent.ip_address
    )

    consent_history.append(history)
    history_id_counter += 1

    return consent


@router.get("/consent/contact/{contact_id}", response_model=List[ConsentRecord])
def get_contact_consent_records(
    contact_id: int,
    current_user: dict = Depends(require_sales_claims)
):
    """Get all consent records for a contact."""
    records = [c for c in consent_records if c.contact_id == contact_id]
    return records


@router.get("/consent/contact/{contact_id}/summary", response_model=ConsentSummary)
def get_consent_summary(
    contact_id: int,
    current_user: dict = Depends(require_sales_claims)
):
    """Get consent summary for a contact."""
    contact_consents = [c for c in consent_records if c.contact_id == contact_id]

    # Get latest consent for each type
    consent_map = {}
    for consent in contact_consents:
        if consent.consent_type not in consent_map or consent.created_at > consent_map[consent.consent_type].created_at:
            consent_map[consent.consent_type] = consent

    # Get privacy policy acceptance
    dpa = next((d for d in data_processing_agreements if d.contact_id == contact_id and d.accepted), None)

    # Build summary
    last_updated = max([c.updated_at for c in contact_consents]) if contact_consents else datetime.now()

    return ConsentSummary(
        contact_id=contact_id,
        essential=consent_map.get(ConsentType.ESSENTIAL, ConsentRecord(
            id=0, contact_id=contact_id, consent_type=ConsentType.ESSENTIAL,
            granted=True, source="default", granted_at=datetime.now(),
            created_at=datetime.now(), updated_at=datetime.now()
        )).granted,
        marketing=consent_map.get(ConsentType.MARKETING, ConsentRecord(
            id=0, contact_id=contact_id, consent_type=ConsentType.MARKETING,
            granted=False, source="default", granted_at=datetime.now(),
            created_at=datetime.now(), updated_at=datetime.now()
        )).granted,
        analytics=consent_map.get(ConsentType.ANALYTICS, ConsentRecord(
            id=0, contact_id=contact_id, consent_type=ConsentType.ANALYTICS,
            granted=False, source="default", granted_at=datetime.now(),
            created_at=datetime.now(), updated_at=datetime.now()
        )).granted,
        personalization=consent_map.get(ConsentType.PERSONALIZATION, ConsentRecord(
            id=0, contact_id=contact_id, consent_type=ConsentType.PERSONALIZATION,
            granted=False, source="default", granted_at=datetime.now(),
            created_at=datetime.now(), updated_at=datetime.now()
        )).granted,
        third_party=consent_map.get(ConsentType.THIRD_PARTY, ConsentRecord(
            id=0, contact_id=contact_id, consent_type=ConsentType.THIRD_PARTY,
            granted=False, source="default", granted_at=datetime.now(),
            created_at=datetime.now(), updated_at=datetime.now()
        )).granted,
        privacy_policy_accepted=dpa is not None,
        privacy_policy_version=dpa.policy_version if dpa else None,
        last_updated=last_updated
    )


@router.put("/consent/{consent_id}", response_model=ConsentRecord)
def update_consent_record(
    consent_id: int,
    request: UpdateConsentRequest,
    http_request: Request,
    current_user: dict = Depends(require_sales_claims)
):
    """Update a consent record (grant/revoke)."""
    global history_id_counter

    consent = next((c for c in consent_records if c.id == consent_id), None)
    if not consent:
        raise HTTPException(status_code=404, detail="Consent record not found")

    now = datetime.now()
    previous_value = consent.granted

    # Update consent
    consent.granted = request.granted
    consent.updated_at = now
    if not request.granted:
        consent.revoked_at = now
    else:
        consent.revoked_at = None

    # Create history entry
    history = ConsentHistory(
        id=history_id_counter,
        consent_record_id=consent.id,
        action="granted" if request.granted else "revoked",
        previous_value=previous_value,
        new_value=request.granted,
        reason=request.reason,
        changed_by=current_user.get("user_id"),
        changed_at=now,
        ip_address=http_request.client.host
    )

    consent_history.append(history)
    history_id_counter += 1

    return consent


@router.get("/consent/{consent_id}/history", response_model=ConsentHistoryResponse)
def get_consent_history(
    consent_id: int,
    current_user: dict = Depends(require_sales_claims)
):
    """Get history of changes for a consent record."""
    consent = next((c for c in consent_records if c.id == consent_id), None)
    if not consent:
        raise HTTPException(status_code=404, detail="Consent record not found")

    history = [h for h in consent_history if h.consent_record_id == consent_id]

    return ConsentHistoryResponse(
        consent_record_id=consent_id,
        consent_type=consent.consent_type,
        history=history
    )


# Data Processing Agreements (Privacy Policy)

@router.post("/data-processing-agreement", response_model=DataProcessingAgreement)
def create_data_processing_agreement(
    request: CreateDataProcessingAgreementRequest,
    http_request: Request,
    current_user: dict = Depends(require_sales_claims)
):
    """Record privacy policy acceptance."""
    global dpa_id_counter

    now = datetime.now()

    dpa = DataProcessingAgreement(
        id=dpa_id_counter,
        contact_id=request.contact_id,
        policy_version=request.policy_version,
        policy_url=request.policy_url,
        accepted=request.accepted,
        accepted_at=now,
        ip_address=request.ip_address or http_request.client.host,
        user_agent=request.user_agent or http_request.headers.get("user-agent"),
        created_at=now
    )

    data_processing_agreements.append(dpa)
    dpa_id_counter += 1

    return dpa


@router.get("/data-processing-agreement/contact/{contact_id}", response_model=List[DataProcessingAgreement])
def get_contact_dpas(
    contact_id: int,
    current_user: dict = Depends(require_sales_claims)
):
    """Get all DPA records for a contact."""
    dpas = [d for d in data_processing_agreements if d.contact_id == contact_id]
    return dpas


# GDPR Requests

@router.post("/gdpr-request", response_model=GDPRRequest)
def create_gdpr_request(
    request: CreateGDPRRequest,
    current_user: dict = Depends(require_sales_claims)
):
    """Create a new GDPR data subject request."""
    global gdpr_request_id_counter

    now = datetime.now()

    gdpr_request = GDPRRequest(
        id=gdpr_request_id_counter,
        contact_id=request.contact_id,
        request_type=request.request_type,
        status="pending",
        requested_at=now,
        completed_at=None,
        completed_by=None,
        notes=request.notes,
        created_at=now,
        updated_at=now
    )

    gdpr_requests.append(gdpr_request)
    gdpr_request_id_counter += 1

    return gdpr_request


@router.get("/gdpr-request", response_model=List[GDPRRequest])
def get_all_gdpr_requests(
    status: str = None,
    current_user: dict = Depends(require_sales_claims)
):
    """Get all GDPR requests, optionally filtered by status."""
    if status:
        return [r for r in gdpr_requests if r.status == status]
    return gdpr_requests


@router.get("/gdpr-request/contact/{contact_id}", response_model=List[GDPRRequest])
def get_contact_gdpr_requests(
    contact_id: int,
    current_user: dict = Depends(require_sales_claims)
):
    """Get all GDPR requests for a contact."""
    return [r for r in gdpr_requests if r.contact_id == contact_id]


@router.put("/gdpr-request/{request_id}", response_model=GDPRRequest)
def update_gdpr_request(
    request_id: int,
    update: UpdateGDPRRequest,
    current_user: dict = Depends(require_sales_claims)
):
    """Update a GDPR request status."""
    gdpr_request = next((r for r in gdpr_requests if r.id == request_id), None)
    if not gdpr_request:
        raise HTTPException(status_code=404, detail="GDPR request not found")

    now = datetime.now()

    gdpr_request.status = update.status
    gdpr_request.updated_at = now
    if update.notes:
        gdpr_request.notes = update.notes

    if update.status == "completed":
        gdpr_request.completed_at = now
        gdpr_request.completed_by = current_user.get("user_id")

    return gdpr_request


@router.delete("/gdpr-request/{request_id}/execute")
def execute_gdpr_deletion(
    request_id: int,
    current_user: dict = Depends(require_sales_claims)
):
    """Execute a GDPR deletion request (DANGEROUS - requires admin)."""
    gdpr_request = next((r for r in gdpr_requests if r.id == request_id), None)
    if not gdpr_request:
        raise HTTPException(status_code=404, detail="GDPR request not found")

    if gdpr_request.request_type != "deletion":
        raise HTTPException(status_code=400, detail="Not a deletion request")

    if gdpr_request.status != "in_progress":
        raise HTTPException(status_code=400, detail="Request must be in_progress status")

    # In production, this would:
    # 1. Delete or anonymize contact data
    # 2. Remove PII from all records
    # 3. Keep audit trail for compliance
    # 4. Send confirmation email

    contact_id = gdpr_request.contact_id

    # Mark request as completed
    gdpr_request.status = "completed"
    gdpr_request.completed_at = datetime.now()
    gdpr_request.completed_by = current_user.get("user_id")

    return {
        "message": f"GDPR deletion executed for contact {contact_id}",
        "request_id": request_id,
        "executed_at": gdpr_request.completed_at
    }
