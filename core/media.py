"""core/media.py — ffmpeg ile medya işleme (Faz 4 — D-medya-2).

LAZY/opt-in: yalnız medya-işleme tool'ları çağrılınca devreye girer. ffmpeg yoksa açık ToolError
(zero-load: ffmpeg kullanmayan kurslar etkilenmez). Tüm işlemler subprocess + timeout + temp dosya.
"""

from __future__ import annotations

import asyncio
import os
import shutil
import tempfile

from auth.errors import ToolError

FFMPEG = shutil.which("ffmpeg")
DEFAULT_TIMEOUT = 180


def ffmpeg_available() -> bool:
    return FFMPEG is not None


async def _run(args: list[str], timeout: int = DEFAULT_TIMEOUT) -> None:
    if not FFMPEG:
        raise ToolError("media_unavailable", "Bu sunucuda ffmpeg yok (medya işleme devre dışı)")
    proc = await asyncio.create_subprocess_exec(
        FFMPEG, "-y", "-hide_banner", "-loglevel", "error", *args,
        stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.PIPE,
    )
    try:
        _, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        raise ToolError("media_timeout", f"ffmpeg {timeout}s sınırını aştı")
    if proc.returncode != 0:
        raise ToolError("media_error", f"ffmpeg hata: {err.decode('utf-8', 'ignore')[-300:]}")


def _ext(filename: str, default: str) -> str:
    e = (filename.rsplit(".", 1)[-1] if "." in filename else "").lower()
    return e or default


async def image_audio_to_video(image: bytes, audio: bytes, *, img_ext: str = "png",
                               aud_ext: str = "mp3") -> bytes:
    """Sabit görsel + ses → mp4 (slayt videosu). Süre = ses süresi; tarayıcı-güvenli H.264/AAC."""
    with tempfile.TemporaryDirectory() as d:
        ip = os.path.join(d, f"i.{img_ext}")
        ap = os.path.join(d, f"a.{aud_ext}")
        op = os.path.join(d, "o.mp4")
        with open(ip, "wb") as f:
            f.write(image)
        with open(ap, "wb") as f:
            f.write(audio)
        await _run([
            "-loop", "1", "-i", ip, "-i", ap,
            "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
            "-vf", "scale='min(1280,iw)':-2,pad=ceil(iw/2)*2:ceil(ih/2)*2",
            "-c:a", "aac", "-b:a", "128k", "-shortest", op,
        ])
        with open(op, "rb") as f:
            return f.read()


async def extract_poster(video: bytes, *, ext: str = "mp4") -> bytes:
    """Videonun temsili karesi → jpg (poster)."""
    with tempfile.TemporaryDirectory() as d:
        vp = os.path.join(d, f"v.{ext}")
        op = os.path.join(d, "p.jpg")
        with open(vp, "wb") as f:
            f.write(video)
        await _run(["-i", vp, "-vf", "thumbnail", "-frames:v", "1", op], timeout=60)
        with open(op, "rb") as f:
            return f.read()


async def normalize_audio(audio: bytes, *, ext: str = "mp3") -> bytes:
    """Sesi tarayıcı-güvenli mp3'e normalize/transcode et (44.1kHz, 128k)."""
    with tempfile.TemporaryDirectory() as d:
        ap = os.path.join(d, f"a.{ext}")
        op = os.path.join(d, "o.mp3")
        with open(ap, "wb") as f:
            f.write(audio)
        await _run(["-i", ap, "-c:a", "libmp3lame", "-b:a", "128k", "-ar", "44100", op], timeout=120)
        with open(op, "rb") as f:
            return f.read()


async def mux_audio(video: bytes, audio: bytes, *, vid_ext: str = "mp4",
                    aud_ext: str = "mp3") -> bytes:
    """Sessiz video + ses → sesli mp4 (en kısa olana kırp). Faz 10 — narration mix."""
    with tempfile.TemporaryDirectory() as d:
        vp = os.path.join(d, f"v.{vid_ext}")
        ap = os.path.join(d, f"a.{aud_ext}")
        op = os.path.join(d, "o.mp4")
        with open(vp, "wb") as f:
            f.write(video)
        with open(ap, "wb") as f:
            f.write(audio)
        await _run(["-i", vp, "-i", ap, "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                    "-shortest", op])
        with open(op, "rb") as f:
            return f.read()
