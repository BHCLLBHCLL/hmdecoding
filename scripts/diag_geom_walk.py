"""测试 geometry Y=0 记录 stride 遍历."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_node_section, parse_nodes, find_elem_segments
from collections import Counter

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\abaqus\geometry.hm")
ns = find_node_section(p)
row_map = {}
for k in range(ns[1]):
    row_map[k + 1] = u32(p, ns[2] + k * ns[3] + ns[4])
print("node cfg:", ns, "row_count", ns[1])

segs = find_elem_segments(p)
sh = segs[0][0]
cnt = segs[0][3]
print("seg:", segs[0])

CONFIG_NODES = {103: 3, 104: 4, 206: 6, 208: 8}

B = sh + 24
elems = {}
strides = Counter()
markers = Counter()
for k in range(cnt):
    eid = u16(p, B)
    marker = u16(p, B + 12)
    cfg = marker & 0xFF
    n = CONFIG_NODES.get(cfg)
    if n is None:
        print(f"k={k} B={B} (sh+{B-sh}) eid={eid} marker={hex(marker)} cfg={cfg} UNKNOWN")
        for off in range(0, 40, 2):
            print(f"   +{off:3d}: {p[B+off:B+off+2].hex(' ')} u16={u16(p,B+off)}")
        break
    nds = [u16(p, B + 14 + 4 * i) for i in range(n)]
    if not all(1 <= r <= ns[1] for r in nds):
        print(f"k={k} B={B} eid={eid} cfg={cfg} bad nodes {nds}")
        break
    if not (0 < eid < 10_000_000):
        print(f"k={k} B={B} bad eid {eid}")
        break
    elems[eid] = (cfg, nds)
    strides[22 + 4 * n] += 1
    markers[cfg] += 1
    B += 22 + 4 * n

print("parsed:", len(elems))
print("markers(cfg):", dict(markers))
print("strides:", dict(strides))

oracle = {
    1: [20, 21, 61, 19], 2: [19, 61, 62, 18], 3: [21, 22, 63, 61],
    100: [141, 136, 34, 35],
    1000: [945, 951, 963, 954, 1165, 1171, 1183, 1174],
    2000: [2069, 2076, 2086, 2083, 2289, 2296, 2306, 2303],
    4116: [4450, 4449, 4447, 4448, 4670, 4669, 4667, 4668],
}
for eid, exp in oracle.items():
    if eid in elems:
        cfg, rows = elems[eid]
        nids = [row_map.get(r, r) for r in rows]
        ok = (sorted(nids) == sorted(exp))
        print(f"eid={eid} cfg={cfg} rows={rows} nids={nids} match={ok}")
    else:
        print(f"eid={eid} MISSING")
