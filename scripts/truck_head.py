
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64
p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
# dump before 53004
s = 52900
for k in range(0, 130, 4):
    off = s + k
    print(f"  {off-53004:+6d}: {p[off:off+4].hex()} u32={u32(p,off):>10d}")
print("rec0 @53004:", [u32(p, 53004+j*4) for j in range(5)])
print("rec1 @53056:", [u32(p, 53056+j*4) for j in range(5)])
print("rec2 @53108:", [u32(p, 53108+j*4) for j in range(5)])
print("x0:", d64(p, 53024))
