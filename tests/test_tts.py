"""tests/test_tts.py — Faz 11 Piper TTS + synthesize_speech + lokal helper."""

import pytest


def test_piper_available_is_bool():
    from core.tts import piper_available
    assert isinstance(piper_available(), bool)


@pytest.mark.asyncio
async def test_synthesize_unavailable_raises(monkeypatch):
    from core import tts
    from auth.errors import ToolError
    monkeypatch.setattr(tts, "PIPER", None)  # Piper yokmuş gibi
    with pytest.raises(ToolError):
        await tts.synthesize("Merhaba")


@pytest.mark.asyncio
async def test_synthesize_speech_tool_unavailable(monkeypatch):
    import server
    from core import tts
    from fastmcp import Client
    monkeypatch.setattr(tts, "PIPER", None)
    async with Client(server.mcp) as c:
        names = {t.name for t in await c.list_tools()}
        assert "synthesize_speech" in names
        proj = await c.call_tool("create_project", {"title": "T"})
        pid = proj.data.project_id
        with pytest.raises(Exception) as ei:
            await c.call_tool("synthesize_speech", {"project_id": pid, "text": "Merhaba"})
        assert "unavailable" in str(ei.value).lower()


def test_render_guardrail_constant_regression():
    import core.video_render as vr
    assert vr.MAX_DUR == 60.0  # guardrail regresyon koruması


def test_local_media_arg_parser():
    from tools.local_media import build_parser
    p = build_parser()
    ns = p.parse_args(["tts", "--text", "Merhaba", "--out", "a.mp3"])
    assert ns.cmd == "tts" and ns.text == "Merhaba" and ns.out == "a.mp3"
    ns2 = p.parse_args(["render", "--spec", "s.json", "--out", "v.mp4", "--quality", "high"])
    assert ns2.cmd == "render" and ns2.spec == "s.json" and ns2.quality == "high"
