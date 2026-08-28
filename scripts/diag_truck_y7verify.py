"""truck Y=7 config-3 结构验证: 提取 eid/config/节点行号, 对照 oracle."""
import sys
from collections import Counter
sys.path.insert(0, "hmdecoder")
from decoder import (load_payload, u32, u16, d64, find_node_section, parse_nodes,
                     find_elem_segments, is_const, _scan_extra_node_segs)

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
# 构建 row_map (复刻 decode 的 v11-13 路径)
ns = find_node_section(p)
nodes = {}
ns_list = []
if ns:
    n1, b1 = parse_nodes(p, ns)
    if n1:
        nodes = n1
        ns_list.append(ns)
if ns_list:
    main = ns_list[0]
    m_end = main[2] + len(nodes) * main[3]
    excl = [(c[2], c[2] + 8) for c in ns_list]
    for ens in _scan_extra_node_segs(p, excl, lo=max(0, m_end - 256), hi=m_end + 512*1024, min_nid=len(nodes) - 16):
        if any(abs(ens[2] - c[2]) < 32 for c in ns_list):
            continue
        n2, b2 = parse_nodes(p, ens)
        if n2:
            nodes.update(n2)
            ns_list.append(ens)
# 构建 row_map: row -> node id (按段基址排序)
row_map = {}
row = 0
for cfg in sorted(ns_list, key=lambda s: s[2]):
    hi, count, base2, stride, idoff, chain = cfg
    for k in range(count):
        rec = base2 + k * stride
        if rec + stride > len(p):
            break
        nid = u32(p, rec + idoff)
        if not (1 <= nid <= 10_000_000):
            break
        row += 1
        row_map[row] = nid
print("nodes:", len(nodes), "rows:", len(row_map))

# 反向: node id -> row
rev = {nid: r for r, nid in row_map.items()}

# oracle 节点
lines = open("output/ground_truth/truck_elemids.txt").read().splitlines()
gt = set(int(l) for l in lines if l.strip().isdigit())

segs = find_elem_segments(p)
# 找 Y=7 seg 2000310
for sh, segid, cfg71, cnt, X, Y in segs:
    if not (Y == 7 and cnt > 100):
        continue
    print(f"\n=== seg {segid} Y=7 cnt={cnt} ===")
    anchors = []
    j = sh + 16
    while j < sh + 500000:
        if is_const(u32(p, j)):
            anchors.append(j)
        j += 4
    print(f"锚数量: {len(anchors)}")
    ok = 0
    for i in range(min(6, len(anchors))):
        a = anchors[i]
        eid = (u16(p, a + 84) << 16) | u16(p, a + 82)
        tag = u32(p, a + 92) >> 16
        n1 = u32(p, a + 96)
        n2 = u32(p, a + 100)
        nid1 = row_map.get(n1, 0)
        nid2 = row_map.get(n2, 0)
        print(f"  rec{i}: eid={eid} tag={tag} node_rows=[{n1},{n2}] node_ids=[{nid1},{nid2}]")
    break
