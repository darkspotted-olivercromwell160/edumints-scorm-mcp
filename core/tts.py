"""core/tts.py — dahili Piper TTS (Faz 11). Türkçe, çevrimdışı, GPU'suz.

LAZY/opt-in (zero-load): Piper binary veya ses modeli yoksa açık ToolError; import için gerekmez.
Çapraz-MCP medya akışı bundan etkilenmez (kullanıcı kendi TTS MCP'sini de kullanabilir; üst kalite
ya da başka dil için o yol birincildir). Çıktı wav → çağıran taraf media.normalize_audio ile mp3.
"""
from __future__ import annotations

import asyncio
import os
import shutil
import tempfile
from pathlib import Path

from auth.errors import ToolError

PIPER = shutil.which("piper")
DEFAULT_VOICE = os.environ.get("PIPER_VOICE", "/app/voices/tr_TR-dfki-medium.onnx")
SYNTH_TIMEOUT = 120


def _voice_path(voice: str | None = None) -> Path:
    return Path(voice or DEFAULT_VOICE)


def piper_available(voice: str | None = None) -> bool:
    return PIPER is not None and _voice_path(voice).exists()


async def synthesize(text: str, voice: str | None = None,
                     timeout: int = SYNTH_TIMEOUT) -> bytes:
    """Metin → wav bytes (Piper). Metin Piper'a stdin'den verilir."""
    if not PIPER:
        raise ToolError("tts_unavailable", "Bu sunucuda Piper yok (TTS devre dışı)")
    vp = _voice_path(voice)
    if not vp.exists():
        raise ToolError("tts_unavailable", f"Piper ses modeli yok: {vp}")
    text = (text or "").strip()
    if not text:
        raise ToolError("tts_bad_input", "Metin boş")
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "o.wav")
        proc = await asyncio.create_subprocess_exec(
            PIPER, "-m", str(vp), "-f", out,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.PIPE,
        )
        try:
            _, err = await asyncio.wait_for(
                proc.communicate(text.encode("utf-8")), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            raise ToolError("tts_timeout", f"Piper {timeout}s sınırını aştı")
        if proc.returncode != 0 or not os.path.exists(out):
            raise ToolError("tts_error", f"Piper hata: {err.decode('utf-8', 'ignore')[-300:]}")
        with open(out, "rb") as f:
            return f.read()
