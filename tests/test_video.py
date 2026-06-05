"""tests/test_video.py — Faz 10 video backend (modeller, derleyici, render guardrail, tools)."""

import pytest


def test_videospec_validates_and_defaults():
    from core.video import VideoSpec
    spec = VideoSpec.model_validate({
        "scenes": [
            {"duration_sec": 4, "narration_text": "Merhaba",
             "elements": [
                 {"type": "text", "text": "Başlık", "x": 10, "y": 20,
                  "animation": {"preset": "fade", "at": 0, "dur": 0.6}},
                 {"type": "chart", "kind": "bar", "x": 5, "y": 50,
                  "data": [{"label": "A", "value": 30}, {"label": "B", "value": 70}]},
             ]},
        ],
    })
    assert spec.width == 1280 and spec.height == 720 and spec.fps == 30
    s0 = spec.scenes[0]
    assert s0.duration_sec == 4 and s0.narration_text == "Merhaba"
    assert s0.elements[0].type == "text" and s0.elements[0].animation.preset == "fade"
    assert s0.elements[1].type == "chart" and s0.elements[1].kind == "bar"
    assert spec.total_duration() == 4


def test_compiler_emits_clips_and_meta():
    from core.video import VideoSpec
    from components.video_compiler import compile_composition
    spec = VideoSpec.model_validate({"width": 1280, "height": 720, "fps": 30, "scenes": [
        {"duration_sec": 3, "elements": [
            {"type": "text", "text": "Mer<haba", "animation": {"preset": "fade", "at": 0, "dur": 0.5}}]},
        {"duration_sec": 2, "elements": [
            {"type": "chart", "kind": "bar", "data": [{"label": "A", "value": 30},
                                                      {"label": "B", "value": 70}]}]},
    ]})
    out = compile_composition(spec, theme=None)
    assert out.meta["width"] == 1280 and out.meta["fps"] == 30
    assert abs(out.meta["duration"] - 5.0) < 1e-6
    assert 'class="clip"' in out.html and 'data-start="0"' in out.html
    assert 'data-duration="3"' in out.html and 'data-start="3"' in out.html  # 2. sahne t=3
    assert 'id="root" data-composition-id="main"' in out.html  # HyperFrames root composition
    assert 'data-duration="5"' in out.html and 'data-width="1280"' in out.html  # root süre/boyut
    assert 'window.__timelines["main"]' in out.html  # composition-id ile eşleşen timeline
    assert "Mer&lt;haba" in out.html               # metin escape edildi
    assert "<haba" not in out.html.replace("Mer&lt;haba", "")  # ham < sızmadı


def test_guardrails_reject_oversize():
    from core.video import VideoSpec
    from core.video_render import check_guardrails
    from auth.errors import ToolError
    big = VideoSpec.model_validate({"width": 4000, "height": 720,
                                    "scenes": [{"duration_sec": 5, "elements": []}]})
    with pytest.raises(ToolError):
        check_guardrails(big)
    longv = VideoSpec.model_validate({"scenes": [{"duration_sec": 999, "elements": []}]})
    with pytest.raises(ToolError):
        check_guardrails(longv)
    ok = VideoSpec.model_validate({"scenes": [{"duration_sec": 5, "elements": []}]})
    check_guardrails(ok)  # raise etmemeli


def test_hyperframes_available_is_bool():
    from core.video_render import hyperframes_available
    assert isinstance(hyperframes_available(), bool)


@pytest.mark.asyncio
async def test_render_motion_video_unavailable_path(monkeypatch):
    import server
    from core import video_render
    from fastmcp import Client
    monkeypatch.setattr(video_render, "NPX", None)  # HyperFrames yokmuş gibi
    async with Client(server.mcp) as c:
        names = {t.name for t in await c.list_tools()}
        assert "render_motion_video" in names and "render_screen_video" in names
        proj = await c.call_tool("create_project", {"title": "V"})
        pid = proj.data.project_id
        with pytest.raises(Exception) as ei:
            await c.call_tool("render_motion_video", {
                "project_id": pid,
                "video_spec": {"scenes": [{"duration_sec": 3, "elements": [
                    {"type": "text", "text": "Hi"}]}]},
            })
        # spesifik: HyperFrames yok → 'unavailable' (sadece tool adındaki 'video' değil)
        assert "unavailable" in str(ei.value).lower()


@pytest.mark.asyncio
async def test_render_motion_video_guardrail_rejects():
    import server
    from fastmcp import Client
    async with Client(server.mcp) as c:
        proj = await c.call_tool("create_project", {"title": "V"})
        pid = proj.data.project_id
        with pytest.raises(Exception) as ei:
            await c.call_tool("render_motion_video", {
                "project_id": pid,
                "video_spec": {"scenes": [{"duration_sec": 999, "elements": []}]},
            })
        assert "too_long" in str(ei.value).lower() or "süre" in str(ei.value).lower()
