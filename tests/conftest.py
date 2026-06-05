"""tests/conftest.py — test ortamı (server import'undan ÖNCE env ayarlar)."""

import os
import tempfile

# server.py SETTINGS'i import anında okur → env'i burada, import'tan önce kur.
_TMP = tempfile.mkdtemp(prefix="scorm-test-")
os.environ.setdefault("SCORM_AUTH_ENABLED", "0")
os.environ.setdefault("DATA_DIR", _TMP)
os.environ.setdefault("DB_PATH", os.path.join(_TMP, "scorm.db"))
os.environ.setdefault("PUBLIC_BASE_URL", "https://mcp.test/scorm")
os.environ.setdefault("BUILD_SYNC_TIMEOUT_SEC", "20")

import pytest  # noqa: E402

EXAMPLES = os.path.join(os.path.dirname(os.path.dirname(__file__)), "examples")


@pytest.fixture
def examples_dir() -> str:
    return EXAMPLES
