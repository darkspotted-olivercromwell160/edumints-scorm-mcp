// Faz 9 — timeline cue dağıtım sözleşmesi. ENGINE_JS'teki distributeCues ile BİREBİR aynı
// olmalı (templates.py içine kopyalandı). N blok + süre D → artan cue saniyeleri.
import assert from "node:assert";

function distributeCues(n, duration) {
  if (n <= 0) return [];
  const cues = [];
  for (let i = 0; i < n; i++) cues.push((i * duration) / (n + 1));
  return cues;
}

const c = distributeCues(3, 8);
assert.strictEqual(c.length, 3, "3 blok → 3 cue");
assert.strictEqual(c[0], 0, "ilk cue 0");
assert.ok(c[1] > 0 && c[1] < c[2], "artan olmalı");
assert.ok(c[2] < 8, "son cue süreden önce (kuyruk anlatıma kalır)");
assert.deepStrictEqual(distributeCues(0, 8), [], "blok yok → boş");
assert.deepStrictEqual(distributeCues(1, 10), [0], "tek blok → [0]");
console.log("cue dağıtımı OK");
