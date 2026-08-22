
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\2_holes.hm")
print("2_holes len:", len(p))
hits = []
start = 0
while True:
    i = p.find(b"\x88\x00\x00\x00", start)
    if i < 0: break
    n = u32(p, i + 4)
    if 1 <= n <= 10_000_000:
        hits.append((i, n))
    start = i + 1
print("136 hits:", hits[:10])
# any node-ish records? scan for [id][0][0][x] 52B pattern
found = 0
for base in range(0, len(p) - 200, 4):
    ok = 0
    for k in range(10):
        rec = base + k * 52
        if u32(p, rec) >= 1 and u32(p, rec+4) == 0 and u32(p, rec+8) == 0 and abs(d64(p, rec+12)) < 1e9:
            ok += 1
        else:
            break
    if ok >= 8:
        print("  52B node stream at", base, "ok=", ok)
        found += 1
        if found > 3: break
print("found:", found)
# dump head 200B
print("head:", p[:64].hex(" "))
