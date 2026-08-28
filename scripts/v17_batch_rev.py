"""v17 批量逆向: 359 缺失元素, 对每个 eid 命中位置用 oracle 行号匹配真实记录."""
import sys, struct, re
from collections import Counter, defaultdict
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, _collect_node_segments

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")

# 修正 row_map
segs = _collect_node_segments(p)
row_map = {}
row = 0
for hi, cnt, base, stride, idoff, chain in segs:
    for k in range(cnt):
        rec = base + k * stride
        if rec + stride > len(p):
            break
        nid = u32(p, rec)
        x = d64(p, rec + 12)
        if not (1 <= nid <= 10_000_000) or not (abs(x) < 1e9):
            break
        row += 1
        row_map[row] = nid
row_of = {v: k for k, v in row_map.items()}

# 读取 359 缺失元素 oracle
oracle = {}
for line in open("output/ground_truth/v17_missing_full.txt", encoding="utf-8", errors="replace"):
    line = line.strip()
    if not line.startswith("E "):
        continue
    m = re.match(r"E eid=(\d+) config=(\d+) nodes=(.*)", line)
    if not m:
        continue
    eid = int(m.group(1))
    cfg = int(m.group(2))
    nds = [int(x) for x in m.group(3).split()]
    oracle[eid] = (cfg, nds)
print(f"oracle elems: {len(oracle)}")
cfg_dist = Counter(c for c, _ in oracle.values())
print("config dist:", dict(cfg_dist))
nn_dist = Counter(len(n) for _, n in oracle.values())
print("nodes-per-elem dist:", dict(nn_dist))

# 对每个 eid: 找所有 u32 hit, 在窗口 [h, h+160] 统计 oracle row 匹配
results = {}
for eid, (cfg, nds) in sorted(oracle.items()):
    orows = set(row_of.get(n) for n in nds)
    pat = struct.pack("<I", eid)
    hits = []
    j = 0
    while True:
        j = p.find(pat, j)
        if j < 0:
            break
        hits.append(j); j += 1
    best = None
    for h in hits:
        win = min(h + 200, len(p) - 2)
        # u16 匹配计数
        u16hits = []
        for o in range(h + 4, win, 2):
            if u16(p, o) in orows:
                u16hits.append(o)
        # u32 高位匹配 ((row<<16)|flag)
        u32hi = []
        for o in range(h + 4, win, 4):
            v = u32(p, o)
            if (v >> 16) in orows and (v & 0xFFFF) in (0, 1, 2, 3, 4, 8):
                u32hi.append(o)
        score = len(u16hits) + len(u32hi)
        if best is None or score > best[0]:
            best = (score, h, u16hits, u32hi)
    results[eid] = (cfg, nds, best)

# 汇总: 每个 config 的匹配统计
print("\n== match stats by config ==")
for cfg in sorted(set(c for c, _ in oracle.values())):
    es = [e for e, (c, nds, b) in results.items() if c == cfg and b]
    nomatch = [e for e, (c, nds, b) in results.items() if c == cfg and not b]
    ok = [e for e, (c, nds, b) in results.items() if c == cfg and b and b[0] >= 1]
    print(f"config {cfg}: total={len(es)} matched={len(ok)} nomatch={len(nomatch)}")

# 每个 config 找 1-2 个典型样本 dump
print("\n== sample dumps ==")
seen = set()
for eid, (cfg, nds, b) in sorted(results.items()):
    if cfg in seen or not b or b[0] < 1:
        continue
    seen.add(cfg)
    score, h, u16h, u32h = b
    orows = sorted(row_of.get(n) for n in nds)
    print(f"\n--- eid={eid} config={cfg} oracle_nodes={nds} rows={orows}")
    print(f"    best hit @{h} score={score} u16@{u16h[:8]} u32hi@{u32h[:8]}")
    for off in range(0, 80, 4):
        q = h + off
        if q + 4 > len(p):
            break
        v = u32(p, q)
        mark = ""
        if (v >> 16) in orows:
            mark = f" <hirow{(v>>16)}>"
        if u16(p, q) in orows or u16(p, q + 2) in orows:
            mark += f" <u16row>"
        print(f"    +{off:3d}: {p[q:q+4].hex(' ')} u32={v:<10d} u16=({u16(p,q)},{u16(p,q+2)}){mark}")
