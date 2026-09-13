from typing import Annotated

from fastapi import Depends, Header, HTTPException, Response, status

from ..db.repositories.exceptions import MissingVersionError

"""HTTP conditional requests: the `ETag` a read hands out and the `If-Match` a
write must present."""

ETAG_HEADER = "ETag"
IF_MATCH_HEADER = "If-Match"

# A weak validator (`W/"..."`) promises only that two representations are
# semantically equivalent, which is not a claim about the row having been
# written. `xmin` is exact, so what we issue is always strong.
_WEAK_PREFIX = "W/"

# `xmin` is an `xid`: an unsigned 32-bit integer
# Zero is excluded because Postgres reserves it as InvalidTransactionId
_MIN_VERSION, _MAX_VERSION = 1, 2**32 - 1


def format_etag(version: int) -> str:
    """Wrap a row version in the quotes the header syntax requires."""
    return f'"{version}"'


def tag_response(response: Response, version: int) -> None:
    """Attach a row's version to the response the client is about to cache."""
    response.headers[ETAG_HEADER] = format_etag(version)


def require_if_match(
    if_match: Annotated[str | None, Header(alias=IF_MATCH_HEADER)] = None,
) -> int:
    """Turn the `If-Match` header into the bare version the repository compares
    against, and refuse the request if it is absent or unusable."""

    if if_match is None:
        raise MissingVersionError(
            f"This request requires an {IF_MATCH_HEADER} header carrying the "
            "version of the resource being replaced."
        )

    candidate: str = if_match.strip()

    # `*` means "any current representation", i.e. proceed if the row exists at all
    if candidate == "*":
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"{IF_MATCH_HEADER}: * is not supported. Send the version you read.",
        )

    # The header may carry a comma-separated list. Ours are single-row versions.
    if "," in candidate:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"{IF_MATCH_HEADER} must carry exactly one entity tag.",
        )

    if candidate.startswith(_WEAK_PREFIX):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"{IF_MATCH_HEADER} must carry a strong entity tag, not {candidate}.",
        )

    if not (
        candidate.startswith('"') and candidate.endswith('"') and len(candidate) > 2
    ):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Malformed {IF_MATCH_HEADER}: entity tags are quoted.",
        )

    try:
        version = int(candidate[1:-1])
    except ValueError:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Malformed {IF_MATCH_HEADER}: an entity tag issued here is a number.",
        )

    if not _MIN_VERSION <= version <= _MAX_VERSION:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Malformed {IF_MATCH_HEADER}: {version} is not a version any row holds.",
        )

    return version


type RequiredVersion = Annotated[int, Depends(require_if_match)]
