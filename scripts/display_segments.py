import sys, gzip, struct
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm")
def u32(o): return struct.unpack_from("<I", p, o)[0]
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
# 全 payload 扫描 52B 显示记录（不依赖标记，直接找记录流）
# 找所有满足 [d64 合理][id 合理] 的记录
recs = []
i = 0
while i < len(p) - 52:
    x, y, z = d64(i), d64(i + 8), d64(i + 16)
    rid = u32(i + 40)
    if abs(x) < 1000 and abs(y) < 1000 and abs(z) < 1000 and 0 < rid < 2000:
        recs.append((i, rid, x, y, z))
        i += 52
    else:
        i += 4
out.append(f"52B 对齐显示记录数: {len(recs)}")
# 按 id 排序
recs.sort(key=lambda r: r[1])
out.append("id 段:")
seg_start = None
prev = None
for idx, (off, rid, x, y, z) in enumerate(recs):
    if prev is None or rid - prev > 2:
        if seg_start is not None:
            out.append(f"  {seg_start[0]}..{seg_start[1]} (n={seg_start[2]}) 首={seg_start[3]} 尾={seg_start[4]}")
        seg_start = [rid, rid, 1, (round(x,2), round(y,2), round(z,2)), (round(x,2), round(y,2), round(z,2))]
    else:
        seg_start[1] = rid
        seg_start[2] += 1
        seg_start[4] = (round(x,2), round(y,2), round(z,2))
    prev = rid
if seg_start:
    out.append(f"  {seg_start[0]}..{seg_start[1]} (n={seg_start[2]}) 首={seg_start[3]} 尾={seg_start[4]}")
open("output/ground_truth/display_segments.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
