"""v17 系统性逆向: 对缺失元素, 搜 oracle row 的 u32/u16 出现位置, 与 eid hit 共现分析."""
import sys, struct, re
from collections import defaultdict
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, _collect_node_segments

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")
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

oracle = {}
for line in open("output/ground_truth/v17_missing_full.txt", encoding="utf-8", errors="replace"):
    m = re.match(r"E eid=(\d+) config=(\d+) nodes=(.*)", line.strip())
    if m:
        oracle[int(m.group(1))] = (int(m.group(2)), [int(x) for x in m.group(3).split()])

def find_u32(val):
    pat = struct.pack("<I", val)
    out = []
    j = 0
    while True:
        j = p.find(pat, j)
        if j < 0:
            break
        out.append(j); j += 1
    return out

def find_u16(val):
    pat = struct.pack("<H", val)
    out = []
    j = 0
    while True:
        j = p.find(pat, j)
        if j < 0:
            break
        out.append(j); j += 1
    return out

# 对每个 config 类, 取前 3 个样本详细分析
from collections import Counter
cfg_cnt = Counter(c for c, _ in oracle.values())
print("config dist:", dict(cfg_cnt))

sample_by_cfg = defaultdict(list)
for eid, (cfg, nds) in sorted(oracle.items()):
    if len(sample_by_cfg[cfg]) < 3:
        sample_by_cfg[cfg].append((eid, nds))

for cfg, samples in sorted(sample_by_cfg.items()):
    print(f"\n{'='*70}\nCONFIG {cfg}  (total {cfg_cnt[cfg]})")
    for eid, nds in samples:
        rows = [row_of.get(n) for n in nds]
        print(f"  eid={eid} nodes={nds} rows={rows}")
        # eid hits
        eid_hits = find_u32(eid)
        print(f"    eid u32 hits: {eid_hits[:6]}")
        # 每个 oracle row 的 u32/u16 出现
        for r in rows[:4]:
            u32pos = find_u32(r)
            u16pos = find_u16(r & 0xFFFF)
            print(f"    row {r} (lo16={r&0xFFFF}): u32@{u32pos[:4]} u16@{u16pos[:4]}")
