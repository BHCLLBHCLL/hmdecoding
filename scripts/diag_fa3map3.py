"""frame_assembly_3 深挖: 节点数 / 段列表 / @+4与@+8编码 / oracle eid 区间分布."""
import sys
from collections import Counter
sys.path.insert(0, "hmdecoder")
from decoder import (load_payload, u32, u16, d64, find_node_section, parse_nodes,
                     find_elem_segments, _parse_a_type, is_const)

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\frame_assembly_3.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
row_map = {}
for k in range(ns[1]):
    row_map[k + 1] = u32(p, ns[2] + k * ns[3] + ns[4])
segs = find_elem_segments(p)
print("nodes:", len(n1))
print("row_count:", ns[1])
print("total cnt:", sum(s[3] for s in segs), "segs:", len(segs))

# oracle eid 区间分布
lines = open("output/ground_truth/fa3_elemids.txt").read().splitlines()
gt = sorted(int(l) for l in lines if l.strip().isdigit())
print("oracle:", len(gt), "min", gt[0], "max", gt[-1])
# 连续区间
ranges = []
for v in gt:
    if ranges and v == ranges[-1][1] + 1:
        ranges[-1][1] = v
    else:
        ranges.append([v, v])
print("oracle 连续区间数:", len(ranges))
print("前20区间:", ranges[:20])
print("后10区间:", ranges[-10:])
# 缺口
gaps = [r for r in range(1, gt[-1]+1) if r not in set(gt)]
print("缺口数:", len(gaps), "首20:", gaps[:20])

# 每段: @+4 区间 + @+8 high/low 解码
print("\n=== 段汇总 ===")
for sh, segid, cfg71, cnt, X, Y in segs:
    anchor = None
    for s in range(sh + 16, sh + 80):
        if is_const(u32(p, s)):
            anchor = s
            break
    if anchor is None:
        print(f"seg {segid} Y={Y} cnt={cnt}: NO ANCHOR")
        continue
    rec = anchor
    eid4s = []
    v8_hi = []
    v8_lo = []
    for k in range(min(cnt, 3)):
        eid4s.append(u32(p, rec + 4))
        v8 = u32(p, rec + 8)
        v8_hi.append(v8 >> 16)
        v8_lo.append(v8 & 0xFFFF)
        nxt = p.find(b"\xf5\x1f", rec + 24, min(rec + 200, len(p) - 2))
        while nxt >= 0:
            if is_const(u32(p, nxt)):
                break
            nxt = p.find(b"\xf5\x1f", nxt + 1, min(rec + 200, len(p) - 2))
        if nxt < 0:
            break
        rec = nxt
    # 最后一条 @+4
    # 遍历全部拿到首尾
    rec = anchor
    first = u32(p, rec + 4)
    last = first
    for k in range(cnt):
        last = u32(p, rec + 4)
        nxt = p.find(b"\xf5\x1f", rec + 24, min(rec + 200, len(p) - 2))
        while nxt >= 0:
            if is_const(u32(p, nxt)):
                break
            nxt = p.find(b"\xf5\x1f", nxt + 1, min(rec + 200, len(p) - 2))
        if nxt < 0:
            break
        rec = nxt
    print(f"seg {segid} Y={Y} cfg71={cfg71} cnt={cnt} @+4:[{first}..{last}] "
          f"@+8hi:[{v8_hi[0]}..{v8_hi[-1]}] @+8lo:{set(v8_lo)}")
