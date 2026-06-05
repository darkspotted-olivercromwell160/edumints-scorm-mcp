"""components/video_compiler.py — VideoSpec → HyperFrames HTML kompozisyonu + meta.json (Faz 10).

Çıktı: bir index.html (class="clip" data-start/data-duration'lı sahneler + GSAP timeline) ve
meta.json (width/height/fps/duration). HyperFrames timeline'ı kare-kare ilerletir → deterministik.
Tüm metin escape edilir (XSS/kompozisyon bozulmasına karşı).
"""
from __future__ import annotations

import html as _html
from dataclasses import dataclass, field


@dataclass
class Composition:
    html: str
    meta: dict
    image_asset_ids: list[str] = field(default_factory=list)   # assets/ ihtiyacı


_GSAP = "https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"  # HyperFrames offline cache'ler


def _esc(s: str) -> str:
    return _html.escape(s or "", quote=True)


def _anim_tween(sel: str, a) -> str:
    """Bir element için GSAP from-tween üretir (preset → başlangıç durumu)."""
    base = {
        "fade": "opacity:0",
        "slide": "opacity:0, y:40",
        "zoom": "opacity:0, scale:.85",
        "typewriter": "opacity:0",
        "count-up": "opacity:0",
        "none": "opacity:1",
    }.get(a.preset, "opacity:0")
    return f'tl.from("{sel}", {{{base}, duration:{a.dur:g}, ease:"power2.out"}}, {a.at:g});'


def compile_composition(spec, theme=None) -> Composition:
    """VideoSpec → Composition (HTML + meta + gereken görsel asset id'leri)."""
    W, H, FPS = spec.width, spec.height, spec.fps
    surface = "#0f1622"
    if theme is not None and getattr(theme, "color", None) is not None:
        surface = theme.color.surface
    clips: list[str] = []
    tweens: list[str] = []
    imgs: list[str] = []
    t0 = 0.0
    for si, sc in enumerate(spec.scenes):
        bg = sc.background or surface
        inner: list[str] = []
        for ei, el in enumerate(sc.elements):
            eid = f"s{si}e{ei}"
            sel = f"#{eid}"
            style = f"position:absolute;left:{el.x:g}%;top:{el.y:g}%;"
            if getattr(el, "w", None) is not None:
                style += f"width:{el.w:g}%;"
            if el.type == "text":
                style += (f"font-size:{el.size}px;font-weight:{el.weight};"
                          f"text-align:{el.align};color:{el.color or '#fff'};")
                inner.append(f'<div id="{eid}" style="{style}">{_esc(el.text)}</div>')
            elif el.type == "shape":
                style += f"height:{el.h:g}%;background:{el.fill or el.color or '#3b82f6'};"
                if el.shape == "circle":
                    style += "border-radius:50%;"
                inner.append(f'<div id="{eid}" style="{style}"></div>')
            elif el.type == "image":
                imgs.append(el.asset_id)
                inner.append(f'<img id="{eid}" src="assets/{_esc(el.asset_id)}" style="{style}">')
            elif el.type == "icon":
                style += f"width:{el.size}px;height:{el.size}px;color:{el.color or '#fff'};"
                inner.append(f'<div id="{eid}" style="{style}" data-icon="{_esc(el.name)}"></div>')
            elif el.type == "chart":
                inner.append(_chart_html(eid, el, style))
            tweens.append(_anim_tween(sel, el.animation))
        clips.append(
            f'<div id="scene{si}" class="clip" data-start="{t0:g}" '
            f'data-duration="{sc.duration_sec:g}" data-track-index="0" '
            f'style="position:absolute;inset:0;background:{bg};">'
            + "".join(inner) + "</div>"
        )
        t0 += sc.duration_sec

    total = spec.total_duration()
    timeline_js = (
        "const tl = gsap.timeline({paused:true});\n"
        + "\n".join(tweens)
        + '\nwindow.__timelines = window.__timelines || {};'
        + '\nwindow.__timelines["main"] = tl;'   # composition-id ile eşleşir
    )
    # HyperFrames: boyut/süre #root div'de (data-composition-id/width/height/duration).
    root = (
        f'<div id="root" data-composition-id="main" data-start="0" '
        f'data-duration="{total:g}" data-width="{W}" data-height="{H}">'
        + "".join(clips) + "</div>"
    )
    html_doc = (
        f'<!DOCTYPE html><html lang="tr"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width={W}, height={H}">'
        f'<style>*{{margin:0;padding:0;box-sizing:border-box}}'
        f'html,body{{width:{W}px;height:{H}px;overflow:hidden;'
        f'font-family:system-ui,Arial,sans-serif;background:{surface}}}'
        f'.clip{{will-change:transform,opacity}}</style>'
        f'<script src="{_GSAP}"></script></head><body>'
        + root
        + f'<script>{timeline_js}</script></body></html>'
    )
    meta = {"width": W, "height": H, "fps": FPS, "duration": spec.total_duration()}
    return Composition(html=html_doc, meta=meta, image_asset_ids=list(dict.fromkeys(imgs)))


def _chart_html(eid: str, el, style: str) -> str:
    """Basit, deterministik veri-viz (v1): counter (büyük sayı) veya yatay bar grafik."""
    if el.kind == "counter":
        v = el.data[0].value if el.data else 0
        return (f'<div id="{eid}" style="{style}font-size:96px;font-weight:800;color:'
                f'{el.color or "#fff"}" data-count="{v:g}">{v:g}{_esc(el.suffix)}</div>')
    mx = max((d.value for d in el.data), default=1) or 1
    rows = "".join(
        f'<div style="margin:8px 0;color:#fff;font-size:24px">{_esc(d.label)}'
        f'<div style="height:28px;background:{el.color or "#3b82f6"};'
        f'width:{(d.value / mx * 100):.0f}%;border-radius:6px"></div></div>'
        for d in el.data
    )
    width = "60%" if getattr(el, "w", None) is None else f"{el.w:g}%"
    return f'<div id="{eid}" style="{style}width:{width}">{rows}</div>'
