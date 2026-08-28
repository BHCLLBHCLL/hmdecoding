"""检查 cartridge family-1 检测命中数."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, find_node_section, parse_nodes, find_elem_segments

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\cartridge.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
segs = find_elem_segments(p)
print("node section:", ns, "nodes:", len(n1))
print("seg count:", len(segs))

hits = 0
for sh, segid, cfg71, cnt, X, Y in segs:
    for k in range(cnt):
        rec = sh + 24 + k * 0  # 无固定间距, 用 CONST 锚
        break
    # 枚举 CONST
    j = sh + 24
    hi = 1 << 60
    while True:
        c = p.find(b"\xf5\x1f\x24\x70", j, sh + cnt * 200)
        if c < 0:
            break
        if u32(p, c + 8) in (0x02BD0002, 0x02AE0002) and u16(p, c + 12) == 2596:
            hits += 1
        j = c + 1
print("family-1 hits:", hits)
