
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\molding1.hm")
s = 134 + 24 + 40  # header + 40B tail => 198?  try from 134+64=198... actually start 198
# hypothesis: records start at 134+64 = 198, 36B each
s = 198
for k in range(12):
    r = s + k * 36
    if r + 36 > len(p): break
    nid = u32(p, r)
    x = d64(p, r + 12); y = d64(p, r + 20); z = d64(p, r + 28)
    print(f"k={k}: id={nid} a={u32(p,r+4)} b={u32(p,r+8)} x={x:.4g} y={y:.4g} z={z:.4g}")
