
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64
p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\SEAT_MODEL.hm")
for rec in (110293, 110349, 110405, 112925):
    vals = [u32(p, rec + j*4) for j in range(14)]
    print(f"rec@{rec}: {vals}")
    print(f"   x={d64(p,rec):.4g} y={d64(p,rec+8):.4g} z={d64(p,rec+16):.4g}")
