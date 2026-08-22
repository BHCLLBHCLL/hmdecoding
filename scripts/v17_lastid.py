
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")
base = 197811
last = u32(p, base + (116733) * 68)
print("first block last id:", last)
# check mark distribution in first block
marks = {}
for k in range(116734):
    m = u32(p, base + k*68 + 8)
    marks[m] = marks.get(m, 0) + 1
print("mark distribution:", dict(sorted(marks.items())))
# search for id = last+1 .. last+5 records via coordinate pattern: [id][0][k][x]
import struct
for nid in range(last + 1, last + 4):
    found = []
    for i in range(8_200_000, len(p) - 24):
        if u32(p, i) == nid and u32(p, i+4) == 0:
            found.append(i)
            if len(found) > 3: break
    print(f"id {nid}: hits at {found[:3]}")
