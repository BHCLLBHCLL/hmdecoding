
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

# WS: check records 41-60
p = load_payload("WS_3.2_3d_tetra_finish.hm")
base = 602393
for k in range(40, 62):
    rec = base + k * 52
    nid = u32(p, rec)
    x = d64(p, rec + 12)
    print(f"  k={k}: id={nid} x={x:.4g}")
