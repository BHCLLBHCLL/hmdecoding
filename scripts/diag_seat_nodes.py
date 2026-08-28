"""SEAT_MODEL 节点段 ID 检查 + 元素节点引用 vs nid."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, find_node_section

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm")
ns = find_node_section(p)
print("ns:", ns)
hi, count, base, stride, idoff, chain = ns
ids = []
for k in range(count):
    rec = base + k * stride
    nid = u32(p, rec + 44) - 1 if chain else u32(p, rec + idoff)
    ids.append(nid)
print("count", count, "first 5:", ids[:5], "last 5:", ids[-5:])
print("min", min(ids), "max", max(ids))
print("unique", len(set(ids)))
# 检查是否有 gap
sorted_ids = sorted(ids)
gaps = [sorted_ids[i] for i in range(1, len(sorted_ids)) if sorted_ids[i] != sorted_ids[i-1] + 1]
print("num non-consecutive transitions:", len(gaps))
# 打印前 10 个 gap 位置
shown = 0
for i in range(1, len(sorted_ids)):
    if sorted_ids[i] != sorted_ids[i-1] + 1:
        print(f"  gap: {sorted_ids[i-1]} -> {sorted_ids[i]}")
        shown += 1
        if shown >= 10:
            break
