"""模拟 decode_elements 内部逻辑, 打印每段结果."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import (load_payload, u32, u16, d64, find_node_section, parse_nodes,
                     _parse_a_type, _parse_a_geom, find_elem_segments)

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
row_map = {}
for k in range(ns[1]):
    row_map[k + 1] = u32(p, ns[2] + k * ns[3] + ns[4])

segs = find_elem_segments(p)
elems = {}
sum_got = 0
for sh, segid, cfg71, cnt, X, Y in segs:
    got = None
    if X == 3:
        got = _parse_a_type(p, sh, cnt, len(n1), row_map)
        if got is None:
            nxt_sh = None
            for (sh2, *_rest) in segs:
                if sh2 > sh:
                    nxt_sh = sh2
                    break
            hi = nxt_sh if nxt_sh else len(p)
            got = _parse_a_geom(p, sh, hi, cnt, len(n1), row_map)
    if got:
        sum_got += len(got)
        elems.update(got)
print(f"sum_got={sum_got} final={len(elems)}")
# 找 sum_got 大的段
for sh, segid, cfg71, cnt, X, Y in segs:
    got = _parse_a_type(p, sh, cnt, len(n1), row_map)
    if got is None:
        print(f"seg {segid} @{sh} Y={Y} cnt={cnt}: NONE")
