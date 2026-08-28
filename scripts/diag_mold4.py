"""molding1 节点段全貌: _collect_node_segments + 缺失节点定位."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, _collect_node_segments, parse_nodes, find_node_section

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\molding1.hm")
segs = _collect_node_segments(p)
print("collected segs:", [(s[2], s[1], s[3]) for s in segs])
nodes = {}
for s in segs:
    n, _ = parse_nodes(p, s)
    nodes.update(n)
print(f"nodes: {len(nodes)}")

# 节点段 @182 92B 分析: 真实记录数
base, stride = 182, 92
# 找 92B 流真实长度: 连续合法
cnt = 0
while base + (cnt + 1) * stride <= len(p):
    rec = base + cnt * stride
    nid = u32(p, rec + 8)
    x = d64(p, rec + 12)
    if 1 <= nid <= 10000000 and abs(x) < 1e9 and u32(p, rec + 4) == 0:
        cnt += 1
    else:
        break
print(f"node stream len (strict): {cnt}")

# 节点段后的 88 个缺失节点: 找 nid 7192..7279 的字节位置
for nid in (7192, 7195, 7200, 7205, 7210, 7215, 7220, 7225, 7230, 7235, 7240, 7245, 7250, 7255, 7260, 7265, 7270, 7275, 7279):
    if nid in nodes:
        continue
    pat = nid.to_bytes(4, "little")
    pos = []
    j = 0
    while True:
        j = p.find(pat, j)
        if j < 0:
            break
        pos.append(j); j += 1
    print(f"nid {nid} missing, bytes @ {pos[:4]}")
