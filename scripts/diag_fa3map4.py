"""验证: frame_assembly_3 真实 eid = u16(rec+10) (即 @+8 高16位)."""
import sys
from collections import Counter
sys.path.insert(0, "hmdecoder")
from decoder import (load_payload, u32, u16, find_node_section, parse_nodes,
                     find_elem_segments, is_const)

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\frame_assembly_3.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
segs = find_elem_segments(p)

lines = open("output/ground_truth/fa3_elemids.txt").read().splitlines()
gt = sorted(int(l) for l in lines if l.strip().isdigit())

# 遍历每段每记录, 提取 @+4 (存储id) 和 @+8hi (高16位)
store_ids = []
hi_ids = []
lo_vals = []
flags = []
for sh, segid, cfg71, cnt, X, Y in segs:
    anchor = None
    for s in range(sh + 16, sh + 80):
        if is_const(u32(p, s)):
            anchor = s
            break
    if anchor is None:
        continue
    rec = anchor
    for k in range(cnt):
        sid = u32(p, rec + 4)
        v8 = u32(p, rec + 8)
        hi = v8 >> 16
        lo = v8 & 0xFFFF
        flag = u32(p, rec + 20)
        store_ids.append(sid)
        hi_ids.append(hi)
        lo_vals.append(lo)
        flags.append(flag >> 16)
        nxt = p.find(b"\xf5\x1f", rec + 24, min(rec + 200, len(p) - 2))
        while nxt >= 0:
            if is_const(u32(p, nxt)):
                break
            nxt = p.find(b"\xf5\x1f", nxt + 1, min(rec + 200, len(p) - 2))
        if nxt < 0:
            break
        rec = nxt

print("records walked:", len(store_ids), "oracle:", len(gt))
print("store_ids == gt ?", sorted(store_ids) == gt)
print("hi_ids == gt ?", sorted(hi_ids) == gt)
print("hi_ids 在 oracle 中的数量:", len(set(hi_ids) & set(gt)), "/", len(set(hi_ids)))
print("store_ids 在 oracle 中的数量:", len(set(store_ids) & set(gt)), "/", len(set(store_ids)))

# hi_ids 与 store_ids 的关系: 是否 hi = store 的某种变换
diff = [h - s for h, s in zip(hi_ids, store_ids)]
print("hi - store 分布:", Counter(diff).most_common(12))

# lo 值与 config 的关系 (flag>>16 - 256 = config)
print("\nconfig (flag>>16-256) 与 lo 值对照:")
pairs = Counter((f - 256, l) for f, l in zip(flags, lo_vals))
for (cfg, lo), c in pairs.most_common(20):
    print(f"  config={cfg} lo={lo}  count={c}")

# 缺失: hi_ids 缺失的 oracle eid
miss = sorted(set(gt) - set(hi_ids))
print("\nhi_ids 缺失 oracle:", len(miss), miss[:20])
extra = sorted(set(hi_ids) - set(gt))
print("hi_ids 多余:", len(extra), extra[:20])
