from httpx import codes

SUCCESS_STATUS_CODES: tuple = (
    codes.OK,  # 200
    codes.MOVED_PERMANENTLY,  # 301
    codes.FOUND,  # 302
    codes.TEMPORARY_REDIRECT,  # 307
    codes.PERMANENT_REDIRECT,  # 308
)

# For unpivoting
KEY_COLUMN_NAME: str = "key"
VALUE_COLUMN_NAME: str = "value"
