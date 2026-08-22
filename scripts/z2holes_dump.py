
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\2_holes.hm")
s = 42990
for k in range(0, 200, 4):
    off = s + k
    print(f"  {off-43015:+5d}: {p[off:off+4].hex()} u32={u32(p,off):>9d} d64={d64(p,off):.4g}")
