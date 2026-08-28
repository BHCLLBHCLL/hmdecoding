"""SEAT_MODEL: 列出所有 997 段头 (含被过滤的)."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm")
pat = b"\xe5\x03\x00\x00"
start = 0
hits = []
while True:
    i = p.find(pat, start)
    if i < 0:
        break
    hits.append(i)
    start = i + 1
print("total 997 markers:", len(hits))
# 只看元素段区域 (seg 0 之后)
for h in hits:
    if h < 2_000_000:
        continue
    segid = u32(p, h + 4); cfg71 = u32(p, h + 8); cnt = u32(p, h + 12)
    X = u32(p, h + 16); Y = u32(p, h + 20)
    print(f"  @ {h}: segid={segid} cfg71={cfg71} cnt={cnt} X={X} Y={Y}")
