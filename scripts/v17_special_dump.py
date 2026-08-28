"""v17 特殊段记录完整 dump + oracle 节点行号对照."""
import sys, struct
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64, find_node_section_struct

p = open("output/ground_truth/v17_payload.bin", "rb").read()

# row_map 重建 (含重复行, 先用于行号反查)
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
row_of = {v: k for k, v in row_map.items()}

# oracle 数据
oracle = {
    131508: (3, [2991373, 2980505]),
    131633: (55, [2911530, 2911535, 2911536, 2911553]),
    131766: (1, [617771]),
    589001: (3, [717301, 741336]),
    589100: (22, [617751, 617756, 617752, 617757]),
    589700: (61, [753656, 758015]),
    589136: (55, [758618, 702778, 702774, 702768, 702770]),
}
print("oracle 节点行号:")
for eid, (cfg, nds) in oracle.items():
    rows = [row_of.get(n) for n in nds]
    print(f"  eid={eid} config={cfg} nodes={nds} rows={rows}")

def dump(pos, lo, hi, label):
    print(f"\n== {label} (eid@{pos})")
    for off in range(lo, hi, 4):
        q = pos + off
        if q < 0 or q + 4 > len(p):
            continue
        v = u32(p, q)
        u = (u16(p, q), u16(p, q + 2))
        d = d64(p, q) if q + 8 <= len(p) else 0
        mark = ""
        if u[1] in (701, 686) and u16(p, q + 2) if False else False:
            pass
        if v == 0x70241FF5:
            mark = " <CONST>"
        if u[0] in (2596, 4644, 6692, 12836):
            mark += f" <MK{u[0]}>"
        if u[1] in (2596, 4644, 6692, 12836, 701, 686):
            mark += f" <mk{u[1]}>"
        # 行号命中
        for eid, (cfg, nds) in oracle.items():
            for n in nds:
                r = row_of.get(n)
                if r is not None and (u[0] == r or u[1] == r or v == r):
                    mark += f" <ROW{r}->nid{n}>"
        try:
            ds = f" d={d:.4g}" if abs(d) < 1e12 and d != 0 else ""
        except Exception:
            ds = ""
        print(f"  {off:+5d}: {p[q:q+4].hex(' ')}  u32={v:<11d} u16={u}{mark}{ds}")

# 各段代表性记录 (eid 位置来自上一脚本)
dump(38005521, -48, 96, "seg6500113 Y=7 eid=131508 config=3")
dump(38019557, -48, 96, "seg6500114 Y=10 eid=131633 config=55")
dump(65225855, -48, 96, "seg800029 Y=7 eid=589001 config=3")
dump(65222687, -48, 96, "seg800027 Y=6 eid=589100 config=22")
dump(65235455, -48, 96, "seg800030 Y=8 eid=589136 config=55")
dump(55054409, -48, 96, "seg700131 Y=4 eid=589700 config=61")
