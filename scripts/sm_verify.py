
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, d64, u32

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\SEAT_MODEL.hm")
# N3 (1008,500,500)
hits = []
for i in range(0, len(p) - 24):
    x, y, z = d64(p, i), d64(p, i+8), d64(p, i+16)
    if abs(x-1008) < 1e-4 and abs(y-500) < 1e-4 and abs(z-500) < 1e-4:
        hits.append(i)
print("N3 hits:", hits[:6])
print("N1@110293 N2@110349 N3@110405? 56B stride check:", 110405 in hits or (hits and hits[0]))
# N48 (1320.5, 125, 500)
hits48 = []
for i in range(0, len(p) - 24):
    x, y, z = d64(p, i), d64(p, i+8), d64(p, i+16)
    if abs(x-1320.5) < 1e-3 and abs(y-125) < 1e-3 and abs(z-500) < 1e-3:
        hits48.append(i)
print("N48 hits:", hits48[:3], "expected at 110293 + 47*56 =", 110293 + 47*56)
