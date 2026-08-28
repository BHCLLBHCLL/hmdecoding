"""truck: 定位缺失高 eid 的字节位置, 找出它们属于哪个段/什么布局."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_elem_segments, is_const

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
segs = find_elem_segments(p)

# 采样缺失 eid (config 混合)
samples = [212715, 213000, 218000, 219669, 219677, 220409, 220411, 222000, 225000, 228633]

# 建立段偏移 -> (segid, Y, cnt) 映射
seg_by_off = {}
for sh, segid, cfg71, cnt, X, Y in segs:
    seg_by_off[sh] = (segid, Y, cnt)

# 每个 sample eid 搜索 u32 值出现位置
for eid in samples:
    pat = eid.to_bytes(4, "little")
    positions = []
    j = 0
    while True:
        j = p.find(pat, j)
        if j < 0:
            break
        positions.append(j)
        j += 1
    # 找最近的段头 (之前的段头)
    best = None
    for sh in sorted(seg_by_off):
        if sh <= positions[0] if positions else True:
            best = sh
        else:
            break
    seginfo = seg_by_off.get(best, ("?", "?", "?")) if best is not None else ("?", "?", "?")
    # 该 eid 出现位置相对段头偏移
    deltas = [f"{pos-best}@{pos}" for pos in positions[:6]]
    print(f"eid={eid} 出现 {len(positions)} 次, 最近段头 segid={seginfo[0]} Y={seginfo[1]} cnt={seginfo[2]}, delta: {deltas[:3]}")
