"""auth/ — çoklu API-key doğrulama + kota + SSRF guard (CONTRACTS.md §4, §6, §6.1)."""

from .errors import ErrorCode, ToolError
from .keys import (
    enforce_project_quota,
    enforce_size_quota,
    parse_bearer,
    verify_key,
)
from .ssrf import (
    DEFAULT_ALLOWED_MIMES,
    assert_safe_url,
    decode_data_uri,
    safe_fetch_asset,
)

__all__ = [
    "ErrorCode",
    "ToolError",
    "verify_key",
    "enforce_project_quota",
    "enforce_size_quota",
    "parse_bearer",
    "assert_safe_url",
    "safe_fetch_asset",
    "decode_data_uri",
    "DEFAULT_ALLOWED_MIMES",
]
