
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16
p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\frame_assembly.hm")
sh = 2388833
s = sh + 24
nxt = None
for j in range(s + 24, s + 400):
    if u32(p, j) == 0x70241FF5:
        nxt = j; break
print("CONST@", s, "next CONST@", nxt, "distance:", nxt - s if nxt else None)
# what is at rec+44..rec+72?
rec = s
for off in (40, 44, 48, 52, 56, 60, 64, 68, 72, 76, 80, 84):
    print(f"  +{off}: {p[rec+off:rec+off+4].hex()} u32={u32(p, rec+off)}")
