
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, d64, u32

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\SEAT_MODEL.hm")
print("== SEAT_MODEL search N1 (1508,500,500):")
hits1 = []
for i in range(0, len(p) - 24):
    x, y, z = d64(p, i), d64(p, i+8), d64(p, i+16)
    if abs(x-1508) < 1e-4 and abs(y-500) < 1e-4 and abs(z-500) < 1e-4:
        hits1.append(i)
print("  N1 hits:", hits1[:6])
for h in hits1[:1]:
    print("  record around N1:")
    for off in range(-40, 80, 4):
        print(f"    {off:+4d}: {p[h+off:h+off+4].hex()} u32={u32(p,h+off):>10d}")
# N2
print("N2 (1508, 0, 500):")
hits2 = []
for i in range(0, len(p) - 24):
    x, y, z = d64(p, i), d64(p, i+8), d64(p, i+16)
    if abs(x-1508) < 1e-4 and abs(y) < 1e-4 and abs(z-500) < 1e-4:
        hits2.append(i)
print("  N2 hits:", hits2[:6])

p2 = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\car_section.hm")
print("\n== car_section head before 235548:")
s = 235448
for k in range(0, 100, 4):
    off = s + k
    print(f"  {off-235548:+6d}: {p2[off:off+4].hex()} u32={u32(p2,off):>10d}")
