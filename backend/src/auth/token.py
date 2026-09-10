import jwt
from pydantic import BaseModel, ConfigDict, Field

from ..dependencies import AuthSettings, get_auth_settings
from ..global_constants import FRONTEND_BASE_URL
from .jwks import get_jwks_client

"""Turn a bearer string into a subject"""

# Deliberately pure and synchronous to make the security-critical part of
# authentication testable on its own, with a self-signed key and no HTTP client.

# Must match `signing_algorithm` in terraform/global/auth.tf.
SIGNING_ALGORITHM = "RS256"  # Asymmetric

CLAIM_NAMESPACE = FRONTEND_BASE_URL

REQUIRED_CLAIMS = ["sub", "exp", "iat", "iss", "aud"]


class AccessToken(BaseModel):
    """The claims this application actually reads"""

    subject: str = Field(alias="sub")

    # Both are set by the Auth0 Action only when the identity provider supplied
    # them, so both are optional. They seed the local row on first sight and are
    # not read again as they are in our database.
    name: str | None = Field(default=None, alias=f"{CLAIM_NAMESPACE}/name")
    email: str | None = Field(default=None, alias=f"{CLAIM_NAMESPACE}/email")

    # Claims arrive under their wire names, so the aliases above are how a real
    # token is read. `validate_by_name` additionally allows the field names, so a
    # test or a dependency override can write `AccessToken(subject=...)` instead
    # of spelling out a namespaced claim URL.
    model_config = ConfigDict(validate_by_name=True, frozen=True)


def decode(token: str) -> AccessToken:
    """
    Verify a bearer token and return what it claims.

    Raises: `jwt.InvalidTokenError`
    Translating that into an HTTP response is the caller's job.
    """

    settings: AuthSettings = get_auth_settings()

    # Reads the unverified header to find the `kid`, then returns the matching
    # public key. Trusting an unverified field here is safe because it only
    # selects among keys the issuer itself published: a `kid` naming anything
    # else finds no key and raises.
    signing_key = get_jwks_client().get_signing_key_from_jwt(token)

    claims = jwt.decode(
        token,
        signing_key.key,
        algorithms=[SIGNING_ALGORITHM],
        audience=settings.audience,
        issuer=settings.issuer,
        options={
            # Defaults stated so that the whole policy reads in one place
            "verify_exp": True,  # Expiration
            "verify_nbf": True,  # Not before
            "require": REQUIRED_CLAIMS,
        },
    )

    return AccessToken.model_validate(claims)
