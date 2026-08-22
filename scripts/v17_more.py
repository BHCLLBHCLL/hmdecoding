
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")
import struct
# search for id 3481965 followed by [0]
target = struct.pack("<I", 3481965)
hits = []
start = 0
while True:
    i = p.find(target, start)
    if i < 0: break
    if i + 20 <= len(p) and u32(p, i+4) == 0 and 1 <= u32(p, i+8) <= 16 and abs(d64(p, i+12)) < 1e9:
        hits.append(i)
    start = i + 1
print("id 3481965 record hits:", hits[:5])
# also id 3433 (block 2 start) - verify at 2672603
print("check 2672603: id=", u32(p, 2672603), "mark=", u32(p, 2672603+8))
# find mark=3 sub-blocks: scan after block A end for [id][0][3] pattern
pat3 = b"\x00\x00\x00\x00\x03\x00\x00\x00"
c3 = []
start = 0
while True:
    i = p.find(pat3, start)
    if i < 0: break
    base = i - 4
    if base >= 0 and 1 <= u32(p, base) <= 10_000_000:
        c3.append(base)
    start = i + 1
print("[0][3] candidates:", len(c3), "first:", c3[:5])
