"""调试 _parse_a_geom 断链原因."""
import sys, gzip
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64, find_node_section, parse_nodes

raw = open(r"C:\Program Files\Altair\2019\tutorials\hm\wing_section_complete.hm", "rb").read()
p = gzip.decompress(raw[12:])
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
rc = len(n1)
row_map = {}
for k in range(ns[1]):
    row_map[k + 1] = u32(p, ns[2] + k * ns[3] + ns[4])

MARK = b"\xe4\x0b\x04\x1a"
sh = 56330
rec = sh + 24
cnt = 475
elems = {}
for k in range(cnt):
    if u32(p, rec) != 0x1a040be4:
        j = p.find(MARK, rec, min(rec + 200, len(p)))
        if j < 0:
            print(f"break@{k}: header lost @{rec}")
            break
        rec = j
    eid = u32(p, rec + 36)
    nds = []
    for i in range(8):
        r = u32(p, rec + 48 + 4 * i) >> 16
        if not (1 <= r <= rc):
            break
        nds.append(r)
    if not nds:
        print(f"break@{k}: no valid nodes eid={eid} rec={rec} u32@48={[hex(u32(p,rec+48+4*i)) for i in range(4)]}")
        break
    if not (0 < eid < 10_000_000):
        print(f"break@{k}: bad eid {eid} rec={rec}")
        break
    elems[eid] = nds
    j = p.find(MARK, rec + 68, min(rec + 150, len(p)))
    if j < 0:
        print(f"break@{k}: no next mark, rec={rec} eid={eid}")
        # dump 尾部
        for off in range(60, 100, 4):
            q = rec + off
            print(f"   +{off}: {p[q:q+4].hex(' ')}")
        break
    rec = j
print("parsed:", len(elems))
# 检查 106 之后的预期位置
