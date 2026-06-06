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
# Sonsuz TTL-cleaner arka-plan task'ini testte başlatma (CI'da pytest teardown hang'ini önler).
os.environ.setdefault("SCORM_NO_TTL_CLEANER", "1")
# Testler AĞSIZ olmalı: XSD şema fetch'i (imsglobal) CI'da yavaş/asılı kalabilir. SCORM_SCHEMA_DIR'i
# şemasız bir dizine işaret ettir → _ensure_populated None → conformance testi graceful skip eder.
# (XSD doğrulamasını gerçek koşmak için bu env'i unset edip ağa izin ver.)
os.environ.setdefault("SCORM_SCHEMA_DIR", os.path.join(_TMP, "no_schemas"))

import pytest  # noqa: E402

EXAMPLES = os.path.join(os.path.dirname(os.path.dirname(__file__)), "examples")


@pytest.fixture
def examples_dir() -> str:
    return EXAMPLES
