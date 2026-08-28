"""dump molding1 节点流尾部间隙 (661700-666700) 找缺失节点布局."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\molding1.hm")

# 缺失节点位置
for nid in (7192, 7193, 7194, 7195, 7196, 7197, 7198, 7199, 7200, 7270, 7279):
    pat = nid.to_bytes(4, "little")
    j = p.find(pat, 660000, 670000)
    if j >= 0:
        print(f"nid {nid} @{j}: ctx={p[j:j+16].hex(' ')}")
