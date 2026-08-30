
import sys, struct
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\hm-ansys_contact_manager_2-d_tutorial.hm")
x, y, z = 5.6103071211714, 4.9969377916461, 0
hits = []
for i in range(0, len(p) - 24):
    a, b, c = d64(p, i), d64(p, i+8), d64(p, i+16)
    if abs(a - x) < 1e-4 and abs(b - y) < 1e-4 and abs(c - z) < 1e-4:
        hits.append(i)
print("node 232 coord hits:", hits[:5])
for h in hits[:1]:
    print("record around:", h)
    for off in range(-40, 60, 4):
        print(f"  {off:+4d}: {p[h+off:h+off+4].hex()} u32={u32(p,h+off):>10d}")
# id 232 in the coord record?
for h in hits[:1]:
    for off in range(-40, 60, 4):
        if u32(p, h+off) == 232:
            print(f"  id 232 near offset {off}")
