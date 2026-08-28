"""truck: 定位 eid 212715 的字节位置与上下文."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_elem_segments, is_const

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
target = 212715
pat = target.to_bytes(4, "little")

# 查找所有出现位置
pos = []
j = 0
while True:
    j = p.find(pat, j)
    if j < 0:
        break
    pos.append(j)
    j += 1

print(f"eid {target} (0x{target:X}) 出现 {len(pos)} 次")
# 找元素段附近的出现
segs = find_elem_segments(p)
seg_starts = [s[0] for s in segs]
print(f"共 {len(segs)} 个元素段")

for j in pos[:20]:
    # 打印上下文: 前后 32 字节 u32 视图
    ctx = [u32(p, j + 4*i) for i in range(-6, 8)]
    # 判断是否在元素段附近 (CONST 标记 0x70241FF5)
    near_seg = min(seg_starts, key=lambda s: abs(s - j)) if seg_starts else -1
    print(f"  pos={j} near_seg={near_seg} (delta={j-near_seg}) u32ctx={ctx}")
