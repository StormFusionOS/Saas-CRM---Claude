"""Webhook routes for lead ingestion."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from app.db import get_db, InMemoryDB
from app.schemas.webhooks import (
    FacebookLeadPayload,
    GoogleLeadPayload,
    TwilioSMSPayload,
    TwilioVoicePayload,
    WebhookVerification,
)
from app.services.intake import ingest_lead_from_webhook
from app.core.security import (
    verify_facebook_signature,
    verify_twilio_signature,
)
from app.core.config import settings


router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.get("/facebook/leads")
async def verify_facebook_webhook(
    hub_mode: str = None,
    hub_verify_token: str = None,
    hub_challenge: str = None,
):
    """
    Verify Facebook webhook during setup.

    Facebook sends a GET request with verification parameters.
    """
    if hub_mode == "subscribe" and hub_verify_token == settings.FB_VERIFY_TOKEN:
        return int(hub_challenge) if hub_challenge else ""

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Verification failed"
    )


@router.post("/facebook/leads", response_model=WebhookVerification)
async def receive_facebook_lead(
    request: Request,
    payload: FacebookLeadPayload,
    x_hub_signature_256: str = Header(None),
    db: InMemoryDB = Depends(get_db)
) -> WebhookVerification:
    """
    Receive Facebook lead ads webhook.

    Verifies signature and ingests lead data.
    """
    # Verify signature
    body = await request.body()
    if x_hub_signature_256:
        if not verify_facebook_signature(body.decode('utf-8'), x_hub_signature_256):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid signature"
            )

    # Extract lead data
    lead_data = payload.extract_lead_data()
    if not lead_data:
        return WebhookVerification(
            verified=True,
            message="No lead data found in payload"
        )

    # Ingest lead
    try:
        ingest_lead_from_webhook(
            db=db,
            source="FACEBOOK",
            lead_data=lead_data
        )

        return WebhookVerification(
            verified=True,
            message="Lead ingested successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest lead: {str(e)}"
        )


@router.post("/google/leads", response_model=WebhookVerification)
async def receive_google_lead(
    payload: GoogleLeadPayload,
    authorization: str = Header(None),
    db: InMemoryDB = Depends(get_db)
) -> WebhookVerification:
    """
    Receive Google Ads lead form webhook.

    Verifies shared secret and ingests lead.
    """
    # Verify shared secret (simple bearer token check)
    if authorization:
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header"
            )

        token = authorization[7:]
        if token != settings.GOOGLE_WEBHOOK_SECRET:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid secret"
            )

    # Extract contact info
    contact_info = payload.extract_contact_info()

    # Ingest lead
    try:
        ingest_lead_from_webhook(
            db=db,
            source="GOOGLE",
            lead_data={
                "lead_id": payload.lead_id,
                "campaign_id": payload.campaign_id,
                **contact_info
            }
        )

        return WebhookVerification(
            verified=True,
            message="Lead ingested successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest lead: {str(e)}"
        )


@router.post("/twilio/sms", response_model=WebhookVerification)
async def receive_twilio_sms(
    request: Request,
    payload: TwilioSMSPayload,
    x_twilio_signature: str = Header(None),
    db: InMemoryDB = Depends(get_db)
) -> WebhookVerification:
    """
    Receive Twilio SMS webhook.

    Verifies signature and creates interaction.
    """
    # Get full URL
    url = str(request.url)

    # Verify signature
    if x_twilio_signature:
        params = dict(payload)
        if not verify_twilio_signature(url, params, x_twilio_signature):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid signature"
            )

    # Ingest SMS as interaction
    try:
        ingest_lead_from_webhook(
            db=db,
            source="TWILIO",
            lead_data={
                "phone": payload.From,
                "message_sid": payload.MessageSid,
                "body": payload.Body,
                "interaction_type": "SMS",
            }
        )

        return WebhookVerification(
            verified=True,
            message="SMS received"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process SMS: {str(e)}"
        )


@router.post("/twilio/voice", response_model=WebhookVerification)
async def receive_twilio_voice(
    request: Request,
    payload: TwilioVoicePayload,
    x_twilio_signature: str = Header(None),
    db: InMemoryDB = Depends(get_db)
) -> WebhookVerification:
    """
    Receive Twilio voice call webhook.

    Verifies signature and creates interaction.
    """
    # Get full URL
    url = str(request.url)

    # Verify signature
    if x_twilio_signature:
        params = dict(payload)
        if not verify_twilio_signature(url, params, x_twilio_signature):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid signature"
            )

    # Ingest call as interaction
    try:
        ingest_lead_from_webhook(
            db=db,
            source="TWILIO",
            lead_data={
                "phone": payload.From,
                "call_sid": payload.CallSid,
                "call_status": payload.CallStatus,
                "direction": payload.Direction,
                "caller_name": payload.CallerName,
                "interaction_type": "PHONE",
            }
        )

        return WebhookVerification(
            verified=True,
            message="Call logged"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log call: {str(e)}"
        )


__all__ = ["router"]
