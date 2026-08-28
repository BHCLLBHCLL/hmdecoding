"""v17 找 config 1/60 记录: dump 131757/131766/131767/589137/589150 的所有命中上下文."""
import sys, struct
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64, find_node_section_struct, find_elem_segments

p = open("output/ground_truth/v17_payload.bin", "rb").read()
ns_list = []
for ens in find_node_section_struct(p, multi=True):
    if ens[1] >= 50:
        ns_list.append(ens)
row_map = {}
row = 0
for cfg in sorted(ns_list, key=lambda s: s[2]):
    hi, count, base2, stride, idoff, chain = cfg
    for k in range(count):
        rec = base2 + k * stride
        if rec + stride > len(p):
            break
        nid = u32(p, rec + idoff)
        x = d64(p, rec + 12)
        if not (1 <= nid <= 10_000_000) or not (abs(x) < 1e9):
            break
        row += 1
        row_map[row] = nid

segs = sorted(find_elem_segments(p), key=lambda s: s[0])
def seg_of(pos):
    cur = None
    for s in segs:
        if s[0] <= pos:
            cur = s
        else:
            break
    return cur

# 期待: 131757 cfg60 nodes 3462316 3462317 2000000 (rows 116694,116695,36402 in OLD map)
# 131766 cfg1 node 617771 (row 250985); 131767 cfg1 node 623686
# 589137 cfg60 nodes 113187 113188; 589150 cfg60 nodes 200031 225912
row_of = {v: k for k, v in row_map.items()}
print("期待行号 (旧 map):")
print(f"  131757: {[row_of.get(n) for n in (3462316, 3462317, 2000000)]}")
print(f"  131766: {[row_of.get(n) for n in (617771,)]}")
print(f"  131767: {[row_of.get(n) for n in (623686,)]}")
print(f"  589137: {[row_of.get(n) for n in (113187, 113188)]}")
print(f"  589150: {[row_of.get(n) for n in (200031, 225912)]}")

def dump(pos, lo, hi, label):
    s = seg_of(pos)
    print(f"\n== {label} @ {pos} (seg={s[1] if s else '?'} Y={s[5] if s else '?'} rel={pos-s[0] if s else '?'})")
    for off in range(lo, hi, 4):
        q = pos + off
        if q < 0 or q + 4 > len(p):
            continue
        v = u32(p, q)
        u = (u16(p, q), u16(p, q + 2))
        mark = " <CONST>" if v == 0x70241FF5 else ""
        if u[1] in (701, 686):
            mark += f" <{u[1]}>"
        if 100 < v <= 354176 and row_map.get(v):
            mark += f" <r{v}={row_map[v]}>"
        print(f"  {off:+5d}: {p[q:q+4].hex(' ')}  u32={v:<11d} u16={u}{mark}")

dump(38004105, -32, 64, "131757 hit#0")
dump(38068787, -32, 64, "131766 hit#4")
dump(38069511, -32, 64, "131766 hit#5")
dump(40263779, -32, 64, "131767 hit#4")
dump(40536595, -32, 64, "131767 hit#5")
dump(40564561, -32, 64, "589137 hit#0")
dump(40566945, -32, 64, "589150 hit#0")
dump(65754894, -32, 64, "589137 hit#1")
