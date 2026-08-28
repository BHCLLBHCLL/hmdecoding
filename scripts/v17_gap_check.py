"""v17 验证 seg#0 记录 437976 附近的结构与流连续性."""
import sys, struct
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64

p = open("output/ground_truth/v17_payload.bin", "rb").read()
base0, stride0, cnt0 = 197811, 68, 116734

# 检查 seg#0 每条记录的验证状态, 找出是否存在 gap
print("== seg#0 stream validation around k=437970..437990 ==")
for k in range(437970, 437990):
    rec = base0 + k * stride0
    nid = u32(p, rec)
    z4 = u32(p, rec + 4)
    k8 = u32(p, rec + 8)
    x = d64(p, rec + 12)
    ok = (1 <= nid <= 10_000_000 and z4 == 0 and 1 <= k8 <= 16 and abs(x) < 1e9)
    print(f"k={k} @{rec}: nid={nid} z4={z4} k8={k8} x={x:.4f} ok={ok}")

# _struct_stream_len 模拟
cnt = 0
while base0 + cnt * stride0 + stride0 <= len(p):
    rec = base0 + cnt * stride0
    nid = u32(p, rec)
    x = d64(p, rec + 12)
    if 1 <= nid <= 10_000_000 and abs(x) < 1e9 and u32(p, rec + 4) == 0 and 1 <= u32(p, rec + 8) <= 16:
        cnt += 1
    else:
        break
print(f"\nstream len from base: {cnt}")

# 29980203 所在记录
h = 29980203
k_off = (h - base0)
print(f"\n29980203 - base0 = {k_off}; /68 = {k_off/68:.4f}; record k={k_off//68} offset={k_off%68}")

# 完整 dump 29980140..29980460
print("\n== raw dump 29980140..29980460 ==")
for off in range(29980140, 29980460, 4):
    v = u32(p, off)
    print(f"@{off} (+{off-29980140:3d}): {p[off:off+4].hex(' ')}  u32={v:<12d} d={d64(p, off) if off+8 <= len(p) and (off-29980140)%8==0 else ''}")
