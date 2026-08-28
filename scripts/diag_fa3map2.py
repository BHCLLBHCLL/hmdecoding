"""frame_assembly_3 eid 映射深挖: 逐段 dump 记录字节 + @+4/@+18 与 oracle 对照."""
import sys
from collections import Counter
sys.path.insert(0, "hmdecoder")
from decoder import (load_payload, u32, u16, d64, find_node_section, parse_nodes,
                     find_elem_segments, _parse_a_type, is_const, CONST)

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\frame_assembly_3.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
row_map = {}
for k in range(ns[1]):
    row_map[k + 1] = u32(p, ns[2] + k * ns[3] + ns[4])
segs = find_elem_segments(p)
print("nodes:", len(n1), "segs:", len(segs))
print("X:", Counter(s[4] for s in segs), "Y:", Counter(s[5] for s in segs).most_common(10))
print("cfg71:", Counter(s[2] for s in segs).most_common(10))

# oracle eid
lines = open("output/ground_truth/fa3_elemids.txt").read().splitlines()
gt = set(int(l) for l in lines[2:] if l.strip().isdigit())
print("oracle eids:", len(gt), "min", min(gt), "max", max(gt))

# 逐段解析, dump 前 3 条记录的 @+4 值 与 @+18 值
for sh, segid, cfg71, cnt, X, Y in segs:
    got = _parse_a_type(p, sh, cnt, len(n1), row_map)
    n = len(got) if got else 0
    # 找到 CONST 锚
    anchor = None
    for s in range(sh + 16, sh + 80):
        if is_const(u32(p, s)):
            anchor = s
            break
    print(f"\n=== seg {segid} Y={Y} cnt={cnt} -> {n} (anchor={anchor}) ===")
    if anchor is None:
        continue
    rec = anchor
    for k in range(min(cnt, 5)):
        # dump u32 数组 前 20 个
        words = [u32(p, rec + 4 * i) for i in range(20)]
        eid4 = u32(p, rec + 4)
        f1_eid = u16(p, rec + 18) | (u16(p, rec + 20) << 16)
        print(f"  rec{k} @+4={eid4} @+8={u32(p,rec+8)} @+12={u32(p,rec+12)} "
              f"@+18={f1_eid} flag@+28={u32(p,rec+28)}")
        print(f"      u32: {words}")
        # 找下一条 CONST
        nxt = None
        j = p.find(b"\xf5\x1f", rec + 24, min(rec + 200, len(p) - 2))
        while j >= 0:
            if is_const(u32(p, j)):
                nxt = j
                break
            j = p.find(b"\xf5\x1f", j + 1, min(rec + 200, len(p) - 2))
        if nxt is None:
            break
        rec = nxt

# 汇总: 所有段 @+4 读出的 eid 集合 vs oracle
print("\n\n==== 汇总 ====")
dec = {}
for sh, segid, cfg71, cnt, X, Y in segs:
    got = _parse_a_type(p, sh, cnt, len(n1), row_map)
    if got:
        dec.update(got)
missing = sorted(gt - set(dec))
extra = sorted(set(dec) - gt)
print(f"oracle {len(gt)} decoded {len(dec)}")
print(f"missing {len(missing)}: {missing[:30]}")
print(f"extra {len(extra)}: {extra[:30]}")
# decoded eid 范围
decs = sorted(dec)
print(f"decoded eid min/max: {decs[0]} .. {decs[-1]}")
