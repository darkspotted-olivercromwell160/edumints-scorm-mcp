"""core/video.py — programatik video sahne-spec'i (Faz 10). HyperFrames'e derlenir.

Claude yüksek-seviye VideoSpec JSON yazar; sunucu (components.video_compiler) bunu temaya-uygun
HyperFrames HTML kompozisyonuna derler, core.video_render MP4'e render eder. Element konumları
yüzde (0-100) cinsindendir → çözünürlükten bağımsız.
"""
from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field

AnimPreset = Literal["fade", "slide", "zoom", "typewriter", "count-up", "none"]


class Animation(BaseModel):
    preset: AnimPreset = "fade"
    at: float = 0.0          # sahne içinde başlama (sn)
    dur: float = 0.5         # animasyon süresi (sn)


class _ElemBase(BaseModel):
    x: float = 10.0          # sol % (0-100)
    y: float = 10.0          # üst % (0-100)
    w: float | None = None   # genişlik % (opsiyonel)
    color: str | None = None
    animation: Animation = Field(default_factory=Animation)


class TextElement(_ElemBase):
    type: Literal["text"] = "text"
    text: str
    size: int = 48           # px (tuval ölçeğinde)
    weight: int = 700
    align: Literal["left", "center", "right"] = "left"


class ShapeElement(_ElemBase):
    type: Literal["shape"] = "shape"
    shape: Literal["rect", "circle", "line"] = "rect"
    h: float = 10.0          # yükseklik %
    fill: str | None = None


class ImageElement(_ElemBase):
    type: Literal["image"] = "image"
    asset_id: str            # projedeki görsel asset


class IconElement(_ElemBase):
    type: Literal["icon"] = "icon"
    name: str                # lucide ikon adı (play, star, check, ...)
    size: int = 64


class ChartDatum(BaseModel):
    label: str
    value: float


class ChartElement(_ElemBase):
    type: Literal["chart"] = "chart"
    kind: Literal["bar", "line", "pie", "counter"] = "bar"
    data: list[ChartDatum] = Field(default_factory=list)
    suffix: str = ""         # counter için ("%", "₺")


VideoElement = Annotated[
    Union[TextElement, ShapeElement, ImageElement, IconElement, ChartElement],
    Field(discriminator="type"),
]


class VideoScene(BaseModel):
    duration_sec: float = 4.0
    narration_asset_id: str | None = None
    narration_text: str | None = None
    background: str | None = None         # CSS renk; None → tema yüzeyi
    elements: list[VideoElement] = Field(default_factory=list)


class VideoSpec(BaseModel):
    width: int = 1280
    height: int = 720
    fps: int = 30
    scenes: list[VideoScene]

    def total_duration(self) -> float:
        return float(sum(s.duration_sec for s in self.scenes))
