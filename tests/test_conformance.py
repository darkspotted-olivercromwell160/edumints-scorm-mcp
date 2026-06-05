"""tests/test_conformance.py — Faz 1: imsmanifest.xml resmi XSD conformance.

Üretilen 1.2 ve 2004 manifestleri resmi ADL/IMS XSD'lerine karşı doğrulanır (offline, no_network).
Şemalar çevrimdışı (fetch edilemez) ise test atlanır — schema_unavailable bloklamayan uyarıdır.
"""

import pytest

from core.manifest import build_manifest
from core.project import Project, new_project_id, ContentSlide, MCQScreen, Choice


def _proj(ver: str) -> Project:
    p = Project(id=new_project_id(), title=f"Conformance {ver}", scorm_version=ver)
    p.screens = [
        ContentSlide(id="c", title="İçerik", body_html="<p>Merhaba</p>"),
        MCQScreen(id="q", title="Soru", prompt_html="<p>?</p>",
                  options=[Choice(id="a", text_html="1", correct=True),
                           Choice(id="b", text_html="2")]),
    ]
    return p


@pytest.mark.parametrize("ver", ["1.2", "2004"])
def test_manifest_xsd_valid(ver, tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))  # izole şema cache
    import core.schema_validate as sv
    sv._compiled_schema.cache_clear()
    from core.schema_validate import validate_manifest_xsd, SCHEMA_UNAVAILABLE, CONFORMANCE_ERROR
    p = _proj(ver)
    xml = build_manifest(p, file_list=["index.html", "runtime/scorm-again.min.js"]).encode()
    errs = validate_manifest_xsd(xml, ver)
    if any(e.code == SCHEMA_UNAVAILABLE for e in errs):
        pytest.skip("SCORM XSD şemaları çevrimdışı — fetch edilemedi")
    conf = [e for e in errs if e.code == CONFORMANCE_ERROR]
    assert conf == [], f"{ver} XSD ihlali: {[e.message for e in conf]}"
    sv._compiled_schema.cache_clear()


def test_schema_unavailable_graceful_degrade(monkeypatch):
    """Şema yoksa: conformance_error DEĞİL, bloklamayan schema_unavailable UYARISI (sessiz geçmez)."""
    import core.schema_validate as sv
    sv._compiled_schema.cache_clear()
    monkeypatch.setattr(sv, "_ensure_populated", lambda v: None)
    sv._compiled_schema.cache_clear()
    p = _proj("2004")
    xml = build_manifest(p, file_list=["index.html"]).encode()
    errs = sv.validate_manifest_xsd(xml, "2004")
    assert len(errs) == 1 and errs[0].code == sv.SCHEMA_UNAVAILABLE
    sv._compiled_schema.cache_clear()
