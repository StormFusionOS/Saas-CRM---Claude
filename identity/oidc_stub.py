"""
OIDC (OpenID Connect) Stub Implementation

This module provides a complete offline stub for OIDC authentication flows.
Supports Okta, Azure AD, and Google Workspace IdP configurations.

Features:
- Authorization code flow
- Token validation (ID token, access token)
- JWKS key rotation with kid selection
- Nonce and state validation
- Clock skew tolerance
- Audience and issuer verification

Usage:
    from identity.oidc_stub import OIDCProvider, OIDCClient

    # Initialize provider (IdP simulator)
    provider = OIDCProvider(issuer="https://idp.example.com", kid="key-2024-01")

    # Initialize client (your application)
    client = OIDCClient(
        client_id="app-client-id",
        client_secret="app-client-secret",
        redirect_uri="https://app.example.com/callback"
    )

    # Generate authorization URL
    auth_url, state, nonce = client.get_authorization_url(provider)

    # Exchange code for tokens
    tokens = provider.exchange_code(code, client_id, redirect_uri, nonce)

    # Validate ID token
    claims = client.validate_id_token(tokens['id_token'], nonce, provider)
"""

import json
import time
import hashlib
import hmac
import base64
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import secrets as py_secrets


# Supported IdP types
IDP_OKTA = "okta"
IDP_AZURE_AD = "azure_ad"
IDP_GOOGLE_WORKSPACE = "google_workspace"


@dataclass
class OIDCConfiguration:
    """OpenID Connect Discovery metadata"""
    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    userinfo_endpoint: str
    jwks_uri: str
    response_types_supported: list
    subject_types_supported: list
    id_token_signing_alg_values_supported: list
    scopes_supported: list
    token_endpoint_auth_methods_supported: list
    claims_supported: list


@dataclass
class JWK:
    """JSON Web Key"""
    kty: str  # Key type (RSA, EC, oct)
    use: str  # Usage (sig, enc)
    kid: str  # Key ID
    alg: str  # Algorithm (RS256, HS256)
    n: Optional[str] = None  # RSA modulus (for RSA keys)
    e: Optional[str] = None  # RSA exponent (for RSA keys)
    k: Optional[str] = None  # Secret key (for symmetric keys - HMAC)


@dataclass
class IDToken:
    """ID Token claims"""
    iss: str  # Issuer
    sub: str  # Subject (user ID)
    aud: str  # Audience (client ID)
    exp: int  # Expiration time
    iat: int  # Issued at time
    nonce: Optional[str] = None  # Nonce for replay prevention
    email: Optional[str] = None
    name: Optional[str] = None
    preferred_username: Optional[str] = None
    groups: Optional[list] = None
    roles: Optional[list] = None
    # ABAC attributes
    department: Optional[str] = None
    environment: Optional[str] = None
    data_domain: Optional[str] = None


class OIDCProvider:
    """
    OIDC Identity Provider Stub

    Simulates an OIDC IdP (Okta, Azure AD, Google Workspace) for offline testing.
    """

    def __init__(
        self,
        issuer: str,
        kid: str = "default-key-2024",
        idp_type: str = IDP_OKTA,
        clock_skew_seconds: int = 300  # 5 minutes
    ):
        self.issuer = issuer
        self.kid = kid
        self.idp_type = idp_type
        self.clock_skew_seconds = clock_skew_seconds

        # Generate a stub signing key (HS256 for simplicity in stubs)
        # In production, this would be RSA256 keys
        self.signing_key = py_secrets.token_urlsafe(32)

        # Store issued nonces to prevent replay
        self._used_nonces = set()

        # Store authorization codes
        self._auth_codes = {}  # code -> {client_id, redirect_uri, nonce, user_claims}

    def get_discovery_document(self) -> OIDCConfiguration:
        """Return OIDC discovery metadata"""
        base_url = self.issuer

        return OIDCConfiguration(
            issuer=self.issuer,
            authorization_endpoint=f"{base_url}/authorize",
            token_endpoint=f"{base_url}/token",
            userinfo_endpoint=f"{base_url}/userinfo",
            jwks_uri=f"{base_url}/.well-known/jwks.json",
            response_types_supported=["code", "id_token", "code id_token"],
            subject_types_supported=["public"],
            id_token_signing_alg_values_supported=["RS256", "HS256"],
            scopes_supported=["openid", "profile", "email", "groups"],
            token_endpoint_auth_methods_supported=["client_secret_post", "client_secret_basic"],
            claims_supported=["sub", "iss", "aud", "exp", "iat", "nonce", "email", "name", "groups", "roles"]
        )

    def get_jwks(self) -> Dict[str, Any]:
        """Return JSON Web Key Set"""
        # In production, this would be RSA public keys
        # For stub, we return a symmetric key structure (don't use in production!)
        jwk = JWK(
            kty="oct",  # Symmetric key (for stub only)
            use="sig",
            kid=self.kid,
            alg="HS256",
            k=base64.urlsafe_b64encode(self.signing_key.encode()).decode().rstrip("=")
        )

        return {
            "keys": [asdict(jwk)]
        }

    def generate_authorization_code(
        self,
        client_id: str,
        redirect_uri: str,
        nonce: str,
        user_claims: Dict[str, Any]
    ) -> str:
        """Generate an authorization code (stub)"""
        code = py_secrets.token_urlsafe(32)

        self._auth_codes[code] = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "nonce": nonce,
            "user_claims": user_claims,
            "created_at": time.time()
        }

        return code

    def exchange_code_for_tokens(
        self,
        code: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for tokens

        Returns:
            {
                "access_token": str,
                "token_type": "Bearer",
                "expires_in": int,
                "id_token": str,
                "refresh_token": str (optional)
            }
        """
        # Validate code exists
        if code not in self._auth_codes:
            raise ValueError("Invalid authorization code")

        code_data = self._auth_codes[code]

        # Validate client_id and redirect_uri match
        if code_data["client_id"] != client_id:
            raise ValueError("Client ID mismatch")

        if code_data["redirect_uri"] != redirect_uri:
            raise ValueError("Redirect URI mismatch")

        # Check code age (codes expire after 10 minutes)
        if time.time() - code_data["created_at"] > 600:
            raise ValueError("Authorization code expired")

        # Generate tokens
        now = int(time.time())
        user_claims = code_data["user_claims"]

        # Create ID token claims
        id_token_claims = IDToken(
            iss=self.issuer,
            sub=user_claims["sub"],
            aud=client_id,
            exp=now + 3600,  # 1 hour
            iat=now,
            nonce=code_data["nonce"],
            email=user_claims.get("email"),
            name=user_claims.get("name"),
            preferred_username=user_claims.get("preferred_username"),
            groups=user_claims.get("groups", []),
            roles=user_claims.get("roles", []),
            department=user_claims.get("department"),
            environment=user_claims.get("environment"),
            data_domain=user_claims.get("data_domain")
        )

        # Sign ID token (stub implementation with HS256)
        id_token = self._create_jwt(asdict(id_token_claims))

        # Create access token (opaque in stub)
        access_token = py_secrets.token_urlsafe(32)

        # Delete code (one-time use)
        del self._auth_codes[code]

        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "id_token": id_token,
            "refresh_token": py_secrets.token_urlsafe(32)
        }

    def _create_jwt(self, claims: Dict[str, Any]) -> str:
        """Create a JWT (stub implementation with HS256)"""
        # Header
        header = {
            "alg": "HS256",
            "typ": "JWT",
            "kid": self.kid
        }

        # Encode header and claims
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header, separators=(',', ':')).encode()
        ).decode().rstrip("=")

        claims_b64 = base64.urlsafe_b64encode(
            json.dumps(claims, separators=(',', ':')).encode()
        ).decode().rstrip("=")

        # Create signature
        message = f"{header_b64}.{claims_b64}"
        signature = hmac.new(
            self.signing_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")

        return f"{message}.{signature_b64}"

    def validate_nonce(self, nonce: str) -> bool:
        """Check if nonce has been used (replay attack prevention)"""
        if nonce in self._used_nonces:
            return False
        self._used_nonces.add(nonce)
        return True


class OIDCClient:
    """
    OIDC Relying Party (Client) Implementation

    Represents your application consuming OIDC authentication.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        clock_skew_seconds: int = 300
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.clock_skew_seconds = clock_skew_seconds

    def get_authorization_url(
        self,
        provider: OIDCProvider,
        scopes: list = None
    ) -> Tuple[str, str, str]:
        """
        Generate authorization URL for user redirect

        Returns:
            (auth_url, state, nonce)
        """
        if scopes is None:
            scopes = ["openid", "profile", "email", "groups"]

        state = py_secrets.token_urlsafe(32)
        nonce = py_secrets.token_urlsafe(32)

        config = provider.get_discovery_document()

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(scopes),
            "state": state,
            "nonce": nonce
        }

        # In a real implementation, this would construct a proper URL
        # For stub, we just format it
        auth_url = config.authorization_endpoint + "?" + "&".join(
            f"{k}={v}" for k, v in params.items()
        )

        return (auth_url, state, nonce)

    def exchange_code(
        self,
        code: str,
        provider: OIDCProvider
    ) -> Dict[str, Any]:
        """Exchange authorization code for tokens"""
        return provider.exchange_code_for_tokens(
            code=code,
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri
        )

    def validate_id_token(
        self,
        id_token: str,
        expected_nonce: str,
        provider: OIDCProvider
    ) -> Dict[str, Any]:
        """
        Validate ID token

        Validates:
        - Signature
        - Issuer
        - Audience
        - Expiration
        - Nonce
        - Clock skew

        Returns:
            Validated claims dictionary

        Raises:
            ValueError: If validation fails
        """
        # Parse JWT
        parts = id_token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid JWT format")

        header_b64, claims_b64, signature_b64 = parts

        # Decode header
        header_json = base64.urlsafe_b64decode(header_b64 + "==")
        header = json.loads(header_json)

        # Verify kid matches
        if header.get("kid") != provider.kid:
            raise ValueError(f"Invalid key ID: {header.get('kid')} != {provider.kid}")

        # Verify signature
        message = f"{header_b64}.{claims_b64}"
        expected_signature = hmac.new(
            provider.signing_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        expected_signature_b64 = base64.urlsafe_b64encode(expected_signature).decode().rstrip("=")

        if signature_b64 != expected_signature_b64:
            raise ValueError("Invalid signature")

        # Decode claims
        claims_json = base64.urlsafe_b64decode(claims_b64 + "==")
        claims = json.loads(claims_json)

        # Validate issuer
        if claims.get("iss") != provider.issuer:
            raise ValueError(f"Invalid issuer: {claims.get('iss')} != {provider.issuer}")

        # Validate audience
        if claims.get("aud") != self.client_id:
            raise ValueError(f"Invalid audience: {claims.get('aud')} != {self.client_id}")

        # Validate expiration with clock skew
        now = int(time.time())
        exp = claims.get("exp", 0)
        if now > exp + self.clock_skew_seconds:
            raise ValueError(f"Token expired: {now} > {exp} + {self.clock_skew_seconds}")

        # Validate issued at time (not in future)
        iat = claims.get("iat", 0)
        if iat > now + self.clock_skew_seconds:
            raise ValueError(f"Token issued in future: {iat} > {now} + {self.clock_skew_seconds}")

        # Validate nonce
        if claims.get("nonce") != expected_nonce:
            raise ValueError(f"Invalid nonce: {claims.get('nonce')} != {expected_nonce}")

        # Check nonce replay
        if not provider.validate_nonce(expected_nonce):
            raise ValueError("Nonce replay detected")

        return claims


# Helper functions for route integration

def create_stub_user_claims(
    email: str,
    roles: list,
    department: str = None,
    environment: str = None,
    data_domain: str = None
) -> Dict[str, Any]:
    """Create stub user claims for testing"""
    return {
        "sub": hashlib.sha256(email.encode()).hexdigest()[:16],
        "email": email,
        "name": email.split("@")[0].replace(".", " ").title(),
        "preferred_username": email,
        "roles": roles,
        "groups": [f"group-{role.lower()}" for role in roles],
        "department": department,
        "environment": environment,
        "data_domain": data_domain
    }


# Predefined IdP configurations for testing

OKTA_CONFIG = {
    "issuer": "https://dev-12345.okta.com",
    "idp_type": IDP_OKTA
}

AZURE_AD_CONFIG = {
    "issuer": "https://login.microsoftonline.com/tenant-id/v2.0",
    "idp_type": IDP_AZURE_AD
}

GOOGLE_WORKSPACE_CONFIG = {
    "issuer": "https://accounts.google.com",
    "idp_type": IDP_GOOGLE_WORKSPACE
}
