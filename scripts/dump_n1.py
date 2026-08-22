
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\molding1.hm")
s = 182
for k in range(0, 92, 4):
    off = s + k
    print(f"  {k:+3d}: {p[off:off+4].hex()} u32={u32(p,off):>10d} d64={d64(p,off):.5g}")
