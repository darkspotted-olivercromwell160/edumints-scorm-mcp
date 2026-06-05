"""tests/load/load_build.py — build yolu yük testi (CONTRACTS.md §11).

Eşzamanlı build_from_spec çağrılarıyla build yolunu döver; throughput + p50/p95/p99 ölçer.
İki mod:
  - in-memory (vars.): server.mcp'ye doğrudan bağlanır (ağ yok) → çekirdek build kapasitesi
  - remote: MCP_URL ayarlıysa HTTP üzerinden gerçek sunucuya bağlanır

Kullanım:
  python tests/load/load_build.py --concurrency 16 --requests 200
  MCP_URL=https://mcp.edumints.com/scorm/mcp API_KEY=... python tests/load/load_build.py -c 16 -n 200
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import time

# repo kökünü import yoluna ekle (script tests/load/ içinden çalıştırılabilsin)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

SMALL_SPEC = {
    "title": "Yük Testi Kursu",
    "scorm_version": "1.2",
    "tracking": {"completion_rule": "viewed_all_and_passed", "passing_score": 50},
    "screens": [
        {"type": "title_slide", "title": "Başlık"},
        {"type": "content_slide", "title": "İçerik", "body_html": "<p>Metin</p>"},
        {"type": "mcq", "title": "Soru", "prompt_html": "<p>?</p>",
         "options": [{"id": "a", "text_html": "A", "correct": True},
                     {"id": "b", "text_html": "B"}], "points": 10},
        {"type": "summary", "title": "Özet"},
    ],
}


def _make_client():
    from fastmcp import Client

    url = os.environ.get("MCP_URL")
    if url:
        key = os.environ.get("API_KEY", "")
        headers = {"Authorization": f"Bearer {key}"} if key else {}
        return Client(url, headers=headers), f"remote:{url}"
    os.environ.setdefault("SCORM_AUTH_ENABLED", "0")
    import server

    return Client(server.mcp), "in-memory"


async def _worker(client, queue: asyncio.Queue, lat: list[float], errs: list[str]):
    while True:
        try:
            queue.get_nowait()
        except asyncio.QueueEmpty:
            return
        t0 = time.perf_counter()
        try:
            res = await client.call_tool("build_from_spec", {"spec": SMALL_SPEC})
            if res.data.status not in ("done", "running", "queued"):
                errs.append(res.data.status)
        except Exception as e:  # noqa: BLE001
            errs.append(type(e).__name__)
        lat.append(time.perf_counter() - t0)
        queue.task_done()


async def main(concurrency: int, total: int):
    client, mode = _make_client()
    lat: list[float] = []
    errs: list[str] = []
    queue: asyncio.Queue = asyncio.Queue()
    for _ in range(total):
        queue.put_nowait(1)

    async with client:
        # warm-up (lazy init + ilk build)
        await client.call_tool("build_from_spec", {"spec": SMALL_SPEC})
        t0 = time.perf_counter()
        workers = [asyncio.create_task(_worker(client, queue, lat, errs))
                   for _ in range(concurrency)]
        await asyncio.gather(*workers)
        wall = time.perf_counter() - t0

    lat_ms = sorted(x * 1000 for x in lat)
    def pct(p):
        if not lat_ms:
            return 0.0
        return lat_ms[min(len(lat_ms) - 1, int(len(lat_ms) * p))]

    print("=" * 56)
    print(f" scorm-mcp build yük raporu  [{mode}]")
    print("=" * 56)
    print(f" concurrency      : {concurrency}")
    print(f" toplam istek     : {total}")
    print(f" hata             : {len(errs)} {set(errs) if errs else ''}")
    print(f" süre (wall)      : {wall:.2f}s")
    print(f" throughput       : {total / wall:.1f} build/s")
    print(f" gecikme p50      : {pct(0.50):.0f} ms")
    print(f" gecikme p95      : {pct(0.95):.0f} ms")
    print(f" gecikme p99      : {pct(0.99):.0f} ms")
    print(f" gecikme max      : {lat_ms[-1]:.0f} ms" if lat_ms else "")
    print("=" * 56)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--concurrency", type=int, default=16)
    ap.add_argument("-n", "--requests", type=int, default=200)
    args = ap.parse_args()
    asyncio.run(main(args.concurrency, args.requests))
