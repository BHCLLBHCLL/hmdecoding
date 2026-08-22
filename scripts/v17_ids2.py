
import sys, struct
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")
for nid in (707754, 3433, 2003768, 3462324, 3481965):
    target = struct.pack("<I", nid)
    hits = []
    start = 0
    while True:
        i = p.find(target, start)
        if i < 0: break
        if i + 20 <= len(p) and u32(p, i+4) == 0 and 1 <= u32(p, i+8) <= 16:
            hits.append(i)
        start = i + 1
    print(f"id {nid}: hits={hits[:4]}")
