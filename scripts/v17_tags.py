"""从 oracle 学习 tag->config 映射: 对每个样本找真实 hit, 读 tag."""
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

def hits_of(eid):
    pat = struct.pack("<I", eid)
    out = []
    j = 0
    while True:
        j = p.find(pat, j)
        if j < 0:
            break
        out.append(j); j += 1
    return out

# 对每个 eid 每个 hit: 读 tag (u16@+12), 若 eid 的 config 匹配则记录
tag_cfg = defaultdict(lambda: defaultdict(int))
for eid, (cfg, nds) in oracle.items():
    rows_exp = [row_of.get(n) for n in nds]
    for h in hits_of(eid):
        tag = u16(p, h + 12)
        # 检查该 hit 是否为真实记录: +4==0, +8 in (2,3)
        if u32(p, h + 4) == 0 and u32(p, h + 8) in (2, 3):
            tag_cfg[tag][cfg] += 1

print("tag -> config counts:")
for tag in sorted(tag_cfg):
    print(f"  tag {tag}: {dict(tag_cfg[tag])}")

# 构建 tag->config (取最高频)
final = {}
for tag, cdict in tag_cfg.items():
    cfg = max(cdict, key=cdict.get)
    final[tag] = cfg
print("final mapping:", final)
