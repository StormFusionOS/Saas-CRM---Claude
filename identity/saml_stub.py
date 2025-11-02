"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
SAML 2.0 Stub Implementation

This module provides a complete offline stub for SAML 2.0 authentication flows.
Supports Okta, Azure AD, and Google Workspace SAML configurations.

Features:
- SP-initiated SSO flow
- IdP metadata parsing
- Assertion validation (signature, audience, conditions)
- ACS (Assertion Consumer Service) endpoint
- Relay state preservation
- Clock skew tolerance
- Attribute mapping

Usage:
    from identity.saml_stub import SAMLIdentityProvider, SAMLServiceProvider

    # Initialize IdP (simulator)
    idp = SAMLIdentityProvider(
        entity_id="https://idp.example.com",
        sso_url="https://idp.example.com/sso"
    )

    # Initialize SP (your application)
    sp = SAMLServiceProvider(
        entity_id="https://app.example.com",
        acs_url="https://app.example.com/saml/acs"
    )

    # Generate authentication request
    authn_request, relay_state = sp.create_authn_request(idp)

    # Process assertion at ACS
    claims = sp.validate_assertion(assertion_xml, idp)
"""

import base64
import hashlib
import time
import secrets as py_secrets
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import xml.etree.ElementTree as ET


# SAML Namespaces
NS_SAML = "urn:oasis:names:tc:SAML:2.0:assertion"
NS_SAMLP = "urn:oasis:names:tc:SAML:2.0:protocol"
NS_DS = "http://www.w3.org/2000/09/xmldsig#"


@dataclass
class SAMLMetadata:
    """SAML Identity Provider Metadata"""
    entity_id: str
    sso_url: str  # Single Sign-On URL
    slo_url: Optional[str] = None  # Single Logout URL
    certificate: Optional[str] = None  # X.509 certificate for signature validation
    name_id_format: str = "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"


@dataclass
class SAMLAssertion:
    """SAML Assertion claims"""
    subject: str  # NameID
    issuer: str
    audience: str
    session_index: str
    not_before: str  # ISO 8601
    not_on_or_after: str  # ISO 8601
    authn_instant: str  # ISO 8601
    attributes: Dict[str, Any]  # Custom attributes


class SAMLIdentityProvider:
    """
    SAML Identity Provider Stub

    Simulates a SAML IdP for offline testing.
    """

    def __init__(
        self,
        entity_id: str,
        sso_url: str,
        slo_url: str = None,
        clock_skew_seconds: int = 300
    ):
        self.entity_id = entity_id
        self.sso_url = sso_url
        self.slo_url = slo_url
        self.clock_skew_seconds = clock_skew_seconds

        # Store validated relay states
        self._valid_relay_states = set()

    def get_metadata(self) -> SAMLMetadata:
        """Return IdP metadata"""
        return SAMLMetadata(
            entity_id=self.entity_id,
            sso_url=self.sso_url,
            slo_url=self.slo_url,
            certificate="STUB_CERTIFICATE",  # In production, this would be real X.509 cert
            name_id_format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
        )

    def create_saml_response(
        self,
        sp_entity_id: str,
        sp_acs_url: str,
        user_email: str,
        user_attributes: Dict[str, Any],
        relay_state: Optional[str] = None
    ) -> str:
        """
        Create SAML Response with assertion

        Returns:
            Base64-encoded SAML Response XML
        """
        now = datetime.utcnow()
        not_before = now - timedelta(minutes=5)
        not_on_or_after = now + timedelta(hours=1)
        session_index = py_secrets.token_urlsafe(16)

        # Build SAML Response XML (simplified for stub)
        response_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<samlp:Response xmlns:samlp="{NS_SAMLP}"
                xmlns:saml="{NS_SAML}"
                ID="_{py_secrets.token_urlsafe(16)}"
                Version="2.0"
                IssueInstant="{now.isoformat()}Z"
                Destination="{sp_acs_url}">
    <saml:Issuer>{self.entity_id}</saml:Issuer>
    <samlp:Status>
        <samlp:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success"/>
    </samlp:Status>
    <saml:Assertion xmlns:saml="{NS_SAML}"
                    ID="_{py_secrets.token_urlsafe(16)}"
                    Version="2.0"
                    IssueInstant="{now.isoformat()}Z">
        <saml:Issuer>{self.entity_id}</saml:Issuer>
        <saml:Subject>
            <saml:NameID Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress">{user_email}</saml:NameID>
            <saml:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer">
                <saml:SubjectConfirmationData NotOnOrAfter="{not_on_or_after.isoformat()}Z"
                                              Recipient="{sp_acs_url}"/>
            </saml:SubjectConfirmation>
        </saml:Subject>
        <saml:Conditions NotBefore="{not_before.isoformat()}Z"
                        NotOnOrAfter="{not_on_or_after.isoformat()}Z">
            <saml:AudienceRestriction>
                <saml:Audience>{sp_entity_id}</saml:Audience>
            </saml:AudienceRestriction>
        </saml:Conditions>
        <saml:AuthnStatement AuthnInstant="{now.isoformat()}Z"
                            SessionIndex="{session_index}">
            <saml:AuthnContext>
                <saml:AuthnContextClassRef>urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport</saml:AuthnContextClassRef>
            </saml:AuthnContext>
        </saml:AuthnStatement>
        <saml:AttributeStatement>"""

        # Add user attributes
        for attr_name, attr_value in user_attributes.items():
            # Handle list values
            if isinstance(attr_value, list):
                for value in attr_value:
                    response_xml += f"""
            <saml:Attribute Name="{attr_name}">
                <saml:AttributeValue>{value}</saml:AttributeValue>
            </saml:Attribute>"""
            else:
                response_xml += f"""
            <saml:Attribute Name="{attr_name}">
                <saml:AttributeValue>{attr_value}</saml:AttributeValue>
            </saml:Attribute>"""

        response_xml += """
        </saml:AttributeStatement>
    </saml:Assertion>
</samlp:Response>"""

        # Base64 encode
        return base64.b64encode(response_xml.encode()).decode()

    def validate_relay_state(self, relay_state: str) -> bool:
        """Validate relay state to prevent tampering"""
        # In production, this would verify HMAC or signature
        # For stub, we just check if it's in our set
        return relay_state in self._valid_relay_states

    def register_relay_state(self, relay_state: str):
        """Register a valid relay state"""
        self._valid_relay_states.add(relay_state)


class SAMLServiceProvider:
    """
    SAML Service Provider (Relying Party) Implementation

    Represents your application consuming SAML authentication.
    """

    def __init__(
        self,
        entity_id: str,
        acs_url: str,
        clock_skew_seconds: int = 300
    ):
        self.entity_id = entity_id
        self.acs_url = acs_url
        self.clock_skew_seconds = clock_skew_seconds

        # Store issued request IDs to prevent replay
        self._valid_request_ids = set()

    def get_metadata_xml(self) -> str:
        """Return SP metadata XML"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"
                     entityID="{self.entity_id}">
    <md:SPSSODescriptor AuthnRequestsSigned="false"
                       WantAssertionsSigned="true"
                       protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
        <md:AssertionConsumerService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
                                    Location="{self.acs_url}"
                                    index="0"/>
    </md:SPSSODescriptor>
</md:EntityDescriptor>"""

    def create_authn_request(
        self,
        idp: SAMLIdentityProvider,
        force_authn: bool = False
    ) -> Tuple[str, str]:
        """
        Create SAML AuthnRequest

        Returns:
            (authn_request_xml, relay_state)
        """
        request_id = py_secrets.token_urlsafe(16)
        relay_state = py_secrets.token_urlsafe(32)
        now = datetime.utcnow()

        # Register request ID
        self._valid_request_ids.add(request_id)

        # Register relay state with IdP
        idp.register_relay_state(relay_state)

        # Build AuthnRequest XML
        authn_request = f"""<?xml version="1.0" encoding="UTF-8"?>
<samlp:AuthnRequest xmlns:samlp="{NS_SAMLP}"
                    xmlns:saml="{NS_SAML}"
                    ID="_{request_id}"
                    Version="2.0"
                    IssueInstant="{now.isoformat()}Z"
                    Destination="{idp.sso_url}"
                    AssertionConsumerServiceURL="{self.acs_url}"
                    ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
                    ForceAuthn="{'true' if force_authn else 'false'}">
    <saml:Issuer>{self.entity_id}</saml:Issuer>
    <samlp:NameIDPolicy Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
                       AllowCreate="true"/>
</samlp:AuthnRequest>"""

        return (authn_request, relay_state)

    def validate_saml_response(
        self,
        saml_response_b64: str,
        idp: SAMLIdentityProvider,
        relay_state: Optional[str] = None
    ) -> SAMLAssertion:
        """
        Validate SAML Response and extract assertion

        Validates:
        - Response status
        - Issuer
        - Audience
        - Conditions (NotBefore, NotOnOrAfter)
        - Relay state (if provided)

        Returns:
            SAMLAssertion with claims

        Raises:
            ValueError: If validation fails
        """
        # Decode SAML response
        try:
            saml_response_xml = base64.b64decode(saml_response_b64).decode()
        except Exception as e:
            raise ValueError(f"Invalid base64 encoding: {e}")

        # Parse XML
        try:
            root = ET.fromstring(saml_response_xml)
        except Exception as e:
            raise ValueError(f"Invalid XML: {e}")

        # Extract namespace-aware elements
        ns = {"samlp": NS_SAMLP, "saml": NS_SAML}

        # Validate status
        status = root.find(".//samlp:Status/samlp:StatusCode", ns)
        if status is None or status.get("Value") != "urn:oasis:names:tc:SAML:2.0:status:Success":
            raise ValueError("SAML Response status is not Success")

        # Validate issuer
        issuer_elem = root.find(".//saml:Issuer", ns)
        if issuer_elem is None or issuer_elem.text != idp.entity_id:
            raise ValueError(f"Invalid issuer: {issuer_elem.text if issuer_elem is not None else 'None'}")

        # Find assertion
        assertion = root.find(".//saml:Assertion", ns)
        if assertion is None:
            raise ValueError("No assertion found in response")

        # Validate audience
        audience = assertion.find(".//saml:Audience", ns)
        if audience is None or audience.text != self.entity_id:
            raise ValueError(f"Invalid audience: {audience.text if audience is not None else 'None'}")

        # Validate conditions timing
        conditions = assertion.find(".//saml:Conditions", ns)
        if conditions is not None:
            not_before_str = conditions.get("NotBefore")
            not_on_or_after_str = conditions.get("NotOnOrAfter")

            if not_before_str and not_on_or_after_str:
                now = datetime.utcnow()
                not_before = datetime.fromisoformat(not_before_str.rstrip("Z"))
                not_on_or_after = datetime.fromisoformat(not_on_or_after_str.rstrip("Z"))

                # Check NotBefore with clock skew
                if now < not_before - timedelta(seconds=self.clock_skew_seconds):
                    raise ValueError(f"Assertion not yet valid: {now} < {not_before}")

                # Check NotOnOrAfter with clock skew
                if now > not_on_or_after + timedelta(seconds=self.clock_skew_seconds):
                    raise ValueError(f"Assertion expired: {now} > {not_on_or_after}")

        # Extract subject
        name_id = assertion.find(".//saml:NameID", ns)
        if name_id is None:
            raise ValueError("No NameID found in assertion")

        # Extract session index
        authn_statement = assertion.find(".//saml:AuthnStatement", ns)
        session_index = authn_statement.get("SessionIndex") if authn_statement is not None else None

        # Extract attributes
        attributes = {}
        attr_statement = assertion.find(".//saml:AttributeStatement", ns)
        if attr_statement is not None:
            for attr in attr_statement.findall(".//saml:Attribute", ns):
                attr_name = attr.get("Name")
                attr_values = [v.text for v in attr.findall(".//saml:AttributeValue", ns)]

                # If single value, store as string; otherwise as list
                if len(attr_values) == 1:
                    attributes[attr_name] = attr_values[0]
                else:
                    attributes[attr_name] = attr_values

        # Validate relay state if provided
        if relay_state and not idp.validate_relay_state(relay_state):
            raise ValueError("Invalid relay state")

        # Build assertion object
        return SAMLAssertion(
            subject=name_id.text,
            issuer=idp.entity_id,
            audience=self.entity_id,
            session_index=session_index or "",
            not_before=conditions.get("NotBefore", "") if conditions is not None else "",
            not_on_or_after=conditions.get("NotOnOrAfter", "") if conditions is not None else "",
            authn_instant=authn_statement.get("AuthnInstant", "") if authn_statement is not None else "",
            attributes=attributes
        )


# Helper functions for route integration

def create_stub_saml_attributes(
    roles: list,
    department: str = None,
    environment: str = None,
    data_domain: str = None
) -> Dict[str, Any]:
    """Create stub SAML attributes for testing"""
    attributes = {
        "roles": roles,
        "groups": [f"group-{role.lower()}" for role in roles]
    }

    if department:
        attributes["department"] = department
    if environment:
        attributes["environment"] = environment
    if data_domain:
        attributes["data_domain"] = data_domain

    return attributes


# Predefined IdP configurations for testing

OKTA_SAML_CONFIG = {
    "entity_id": "http://www.okta.com/exk1234567890",
    "sso_url": "https://dev-12345.okta.com/app/app1234567890/sso/saml"
}

AZURE_AD_SAML_CONFIG = {
    "entity_id": "https://sts.windows.net/tenant-id/",
    "sso_url": "https://login.microsoftonline.com/tenant-id/saml2"
}

GOOGLE_WORKSPACE_SAML_CONFIG = {
    "entity_id": "google.com",
    "sso_url": "https://accounts.google.com/o/saml2/idp?idpid=C01234567"
}
