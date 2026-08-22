
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")
s = 197823
for off in range(-48, 80, 4):
    print(f"  {off:+4d}: {p[s+off:s+off+4].hex()} u32={u32(p,s+off):>10d}")
