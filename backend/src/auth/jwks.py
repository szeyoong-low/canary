from functools import cache

from jwt import PyJWKClient

from ..dependencies import AuthSettings, get_auth_settings

"""Auth0's public signing keys, fetched once and cached (refetching only on key rotation)"""

# One HTTP round trip is the worst case. It happens on a request thread so it
# must not be allowed to run long, otherwise an unresponsive Auth0 would stall
# the event loop, and with it every other request the process is serving.
# Five seconds is far more than a healthy fetch needs.
JWKS_TIMEOUT_SECONDS: float = 5

# PyJWKClient is synchronous, so a cache miss blocks the event loop for one HTTP
# round trip. Adding httpx + a hand-rolled async cache is a mitigation for later.


@cache
def get_jwks_client() -> PyJWKClient:
    """
    Lazy and cached rather than a module-level constant so that importing the
    package does not demand a populated environment.
    https://pyjwt.readthedocs.io/en/stable/usage.html
    """

    settings: AuthSettings = get_auth_settings()

    return PyJWKClient(
        settings.jwks_uri,
        # Off by default. Enabling it caches each key by its `kid` in an LRU with
        # no expiry, so a token signed by a key we have already seen is verified
        # with no network at all. Expect 100% hit in the steady state.
        #
        # The cost is that a key stays trusted until it is evicted, so a key Auth0
        # revoked early would keep verifying tokens here until the process
        # restarts. Revocation is a blue moon event, and the tokens
        # signed by such a key have their own eight-hour expiry regardless.
        cache_keys=True,
        # Auth0 publishes two or three keys, so the default sixteen is already
        # far more than rotation will ever put in flight.
        max_cached_keys=16,
        # The second-tier cache, holding the whole key set for five minutes.
        # Left at its default: with `cache_keys` on it is only consulted when an
        # unfamiliar `kid` appears, which is exactly the moment a rotation has
        # happened and a fresh fetch is needed.
        cache_jwk_set=True,
        timeout=JWKS_TIMEOUT_SECONDS,
    )
