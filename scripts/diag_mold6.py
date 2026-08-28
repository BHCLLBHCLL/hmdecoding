"""dump molding1 副段区域 661726-666700, 步进 56 检查."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\molding1.hm")
n = len(p)

# 从 661726 起步进 56, 打印每条记录
pos = 661726
cnt = 0
while pos + 56 <= n and cnt < 120:
    nid = u32(p, pos)
    z4 = u32(p, pos + 4)
    x = d64(p, pos + 12)
    ok = 1 <= nid <= 10000000 and z4 == 0 and abs(x) < 1e9
    print(f"@{pos} rel={pos-661726:5d}: nid={nid:<7d} z4={z4} x={x:8.2f} ok={ok} hex={p[pos:pos+16].hex(' ')}")
    if not ok:
        break
    pos += 56
    cnt += 1
print("continuous 56B count:", cnt)
