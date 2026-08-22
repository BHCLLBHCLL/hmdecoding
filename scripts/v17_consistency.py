"""v17 最终一致性检查: 元素节点引用全部有效 + 特殊元素与 oracle 节点全比."""
import sys, re, time
sys.path.insert(0, "hmdecoder")
from decoder import decode

t0 = time.time()
m = decode(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")
print(f"decode t={time.time()-t0:.1f}s nodes={len(m.nodes)} elems={len(m.elements)}")

# 1) 元素节点引用有效性
bad = 0
for eid, (cfg, nds) in m.elements.items():
    if not all(n in m.nodes for n in nds):
        bad += 1
print(f"elems with invalid node refs: {bad}")

# 2) 节点重复/缺失
from collections import Counter
cnt = Counter(m.nodes.keys())
dup = {k: v for k, v in cnt.items() if v > 1}
print(f"duplicate nids: {len(dup)}")

# 3) 特殊元素 (359) 与 oracle 对比
oracle = {}
for line in open("output/ground_truth/v17_missing_full.txt", encoding="utf-8", errors="replace"):
    mm = re.match(r"E eid=(\d+) config=(\d+) nodes=(.*)", line.strip())
    if mm:
        oracle[int(mm.group(1))] = (int(mm.group(2)), [int(x) for x in mm.group(3).split()])
ok = 0
badcfg = 0
for eid, (cfg, onds) in oracle.items():
    if eid not in m.elements:
        continue
    dcfg, dnds = m.elements[eid]
    if dcfg == cfg and sorted(dnds) == sorted(onds):
        ok += 1
    else:
        badcfg += 1
print(f"special elems node/config match: {ok}/{len(oracle)} bad={badcfg}")

# 4) config 分布
from collections import Counter
print("config dist:", Counter(c for c, _ in m.elements.values()).most_common(15))
