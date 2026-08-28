"""SEAT_MODEL: 找全部缺失 eid (1..27503)."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import decode

m = decode(r"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm")
print("nodes:", len(m.nodes), "elems:", len(m.elements))
missing = [e for e in range(1, 27504) if e not in m.elements]
print("num missing:", len(missing))
print("missing eids:", missing[:50])
# 检查是否有 extra (eid > 27503 或 0)
extra = [e for e in m.elements if e > 27503 or e < 1]
print("extra eids:", extra[:50])
