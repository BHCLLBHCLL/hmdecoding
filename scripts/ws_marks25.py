import sys, gzip, struct
from collections import Counter
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
out = []
c = Counter()
for i in range(0, len(p) - 4, 4):
    v = struct.unpack_from("<I", p, i)[0]
    if (v & 0xFF000000) == 0x25000000:
        c[(v >> 16) & 0xFF] += 1
out.append(f"0x25xx0000 家族: {sorted(c.items(), key=lambda x: -x[1])[:15]}")
# 也看 0x24/0x26
for fam in (0x24, 0x26, 0x27):
    c2 = Counter()
    for i in range(0, len(p) - 4, 4):
        v = struct.unpack_from("<I", p, i)[0]
        if (v & 0xFF000000) == (fam << 24):
            c2[(v >> 16) & 0xFF] += 1
    out.append(f"0x{fam:02x}xx0000 家族: {sorted(c2.items(), key=lambda x: -x[1])[:10]}")
# 1d_elements 对照
p2 = D.load_payload("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm")
c3 = Counter()
for i in range(0, len(p2) - 4, 4):
    v = struct.unpack_from("<I", p2, i)[0]
    if (v & 0xFF000000) == 0x25000000:
        c3[(v >> 16) & 0xFF] += 1
out.append(f"1d 0x25xx0000: {sorted(c3.items(), key=lambda x: -x[1])[:10]}")
open("output/ground_truth/ws_marks25.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
