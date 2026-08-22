
import sys, struct
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\c_channel-tcl.hm")
hits = []
start = 0
while True:
    i = p.find(b"\xf5\x1f\x50\x70", start)
    if i < 0: break
    hits.append(i)
    start = i + 1
print("CONST12 hits:", hits[:10])
print("spacing:", [hits[i+1]-hits[i] for i in range(min(9, len(hits)-1))])
# first record full dump
rec = hits[0]
for k in range(0, 72, 4):
    print(f"  +{k:3d}: {p[rec+k:rec+k+4].hex()} u32={u32(p,rec+k):>9d} u16=({u16(p,rec+k):>5d},{u16(p,rec+k+2):>5d})")
