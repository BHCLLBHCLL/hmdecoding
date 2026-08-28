"""调试 seg@56330 第 11 条后断链."""
import sys, gzip
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64

raw = open(r"C:\Program Files\Altair\2019\tutorials\hm\wing_section_complete.hm", "rb").read()
p = gzip.decompress(raw[12:])
MARK = b"\xe4\x0b\x04\x1a"

# 所有命中 + 验证结果
hits = []
j = 56330
while True:
    j = p.find(MARK, j, 91338)
    if j < 0:
        break
    ok = (u32(p, j + 4) == 8 and u32(p, j + 16) == 0x0a040be6 and u32(p, j + 24) == 0x12040084)
    hits.append((j, ok))
    j += 1
valid = [h for h, ok in hits if ok]
print(f"hits: {len(hits)} valid: {len(valid)}")
# 第 10 条后的 valid 位置
for i, (h, ok) in enumerate(hits):
    if 8 <= i <= 14:
        print(f"hit#{i} @{h} rel={h-56330} ok={ok} eid={u32(p, h+36)} +4={u32(p,h+4)} +16={hex(u32(p,h+16))} +24={hex(u32(p,h+24))}")
