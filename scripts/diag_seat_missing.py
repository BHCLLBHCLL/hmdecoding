"""SEAT_MODEL: 全量 decode 后找缺失 eid."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import decode

m = decode(r"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm")
print("nodes:", len(m.nodes), "elems:", len(m.elements))
# oracle 27503, 找缺失
missing = [e for e in range(27495, 27504) if e not in m.elements]
print("missing near end:", missing)
# 检查 27499-27503 的 config/nodes
for e in range(27499, 27504):
    if e in m.elements:
        cfg, nds = m.elements[e]
        print(f"  eid {e}: config={cfg} nodes={nds}")
    else:
        print(f"  eid {e}: MISSING")
