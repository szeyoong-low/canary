import httpx

VALID_STATUS_CODE = [
    httpx.codes.OK,  # 200
    httpx.codes.MOVED_PERMANENTLY,  # 301
    httpx.codes.FOUND,  # 302
    httpx.codes.TEMPORARY_REDIRECT,  # 307
    httpx.codes.PERMANENT_REDIRECT,  # 308
]
