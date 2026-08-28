"""v17 缺口诊断: 逐节点段/逐元素段统计, 定位缺失的 2 节点与 656 单元."""
import sys, time, json
sys.path.insert(0, "hmdecoder")
from decoder import (load_payload, u32, u16, d64, find_node_section_struct,
                     parse_nodes, find_elem_segments, _parse_a_type, _parse_b_type,
                     _parse_b_slots, _struct_stream_len)

PATH = sys.argv[1] if len(sys.argv) > 1 else \
    r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm"
NAME = PATH.split("\\")[-1].replace(".hm", "")
log = open(f"output/ground_truth/v17_gap_{NAME}.txt", "w")
def T(m, t0):
    s = f"{m}: {time.time()-t0:.1f}s"
    print(s); log.write(s + "\n"); log.flush()

p = load_payload(PATH)
T(f"payload: {len(p)} bytes", time.time())

# ---- 节点段全景: multi 扫描 + 无 50 条过滤 ----
t0 = time.time()
segs_raw = find_node_section_struct(p, multi=True)
T(f"struct segs (filtered>=50): {len(segs_raw)}", t0)
nodes = {}
ns_list = []
for ens in segs_raw:
    if ens[1] < 50:
        continue
    n2, _ = parse_nodes(p, ens)
    if n2:
        nodes.update(n2)
        ns_list.append(ens)
for ens in sorted(ns_list, key=lambda s: s[2]):
    hi, cnt, base, stride, idoff, chain = ens
    first = u32(p, base + idoff); last = u32(p, base + (cnt-1)*stride + idoff)
    log.write(f"NODESEG base={base} cnt={cnt} stride={stride} id_range={first}..{last}\n")
log.write(f"NODES total={len(nodes)}\n"); log.flush()

# row_map (与 decode() 相同逻辑)
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
log.write(f"ROWMAP rows={row}\n"); log.flush()

# ---- 元素段全景 ----
esegs = find_elem_segments(p)
log.write(f"ESEGS total={len(esegs)} sum_cnt={sum(s[3] for s in esegs)}\n")
for (sh, segid, cfg71, cnt, X, Y) in esegs:
    if X == 3:
        got = _parse_a_type(p, sh, cnt, len(nodes), row_map)
    else:
        got = _parse_b_type(p, sh, cnt, len(nodes), row_map, Y)
        got2 = _parse_b_slots(p, sh, cnt, len(nodes), row_map, Y)
        if got2 and (got is None or len(got2) > len(got)):
            got = got2
    n = len(got) if got else 0
    tag = "OK" if n >= cnt else "SHORT"
    log.write(f"ESEG sh={sh} segid={segid} cfg={cfg71} cnt={cnt} X={X} Y={Y} got={n} {tag}\n")
log.flush()
elems = {}
for (sh, segid, cfg71, cnt, X, Y) in esegs:
    if X == 3:
        got = _parse_a_type(p, sh, cnt, len(nodes), row_map)
    else:
        got = _parse_b_type(p, sh, cnt, len(nodes), row_map, Y)
        got2 = _parse_b_slots(p, sh, cnt, len(nodes), row_map, Y)
        if got2 and (got is None or len(got2) > len(got)):
            got = got2
    if got:
        elems.update(got)
T(f"ELEMS total={len(elems)} (unique eids)", t0)
log.close()
