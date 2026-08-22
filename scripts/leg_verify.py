import sys
sys.path.insert(0, ".")
from hmdecoder import decode
m = decode("C:/Program Files/Altair/2019/tutorials/hm/interfaces/madymo/leg_geom.hm")
GT = {2: (0.0, 0.0, -0.3), 4: (0.0, 0.0, -0.85), 6: (0.16, 0.0, -1.03), 7: (0.42, 0.0, -1.0)}
ok = 0
for nid, (x, y, z) in GT.items():
    n = m.nodes.get(nid)
    if n and abs(n.x - x) < 1e-9 and abs(n.y - y) < 1e-9 and abs(n.z - z) < 1e-9:
        ok += 1
    else:
        print("bad:", nid, n)
print(f"leg_geom nodes verified: {ok}/4")
