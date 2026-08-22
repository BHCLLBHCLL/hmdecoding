import sys
sys.path.insert(0, ".")
from hmdecoder import decode
m = decode("WS_3.2_3d_tetra_finish.hm")
elem_ok = node_ok = 0
elem_bad = []; node_bad = []
for line in open("output/ground_truth/ws_validate.log", encoding="utf-8").read().splitlines():
    parts = line.split()
    if parts[0] == "elem" and len(parts) == 7:
        eid = int(parts[1])
        cfg = int(parts[2].split("=")[1])
        quad = tuple(int(x.split("=")[1]) for x in parts[3:7])
        e = m.elements.get(eid)
        dec = tuple(e.nodes) + (0,) * (4 - len(e.nodes)) if e else None
        if dec == quad:
            elem_ok += 1
        else:
            elem_bad.append((eid, dec, quad, cfg))
    elif parts[0] == "node" and len(parts) == 5:
        nid = int(parts[1].rstrip(":"))
        xyz = tuple(float(x) for x in parts[2:5])
        n = m.nodes.get(nid)
        if n and abs(n.x - xyz[0]) < 1e-6 and abs(n.y - xyz[1]) < 1e-6 and abs(n.z - xyz[2]) < 1e-6:
            node_ok += 1
        else:
            node_bad.append((nid, (n.x, n.y, n.z) if n else None, xyz))
print(f"elements: {elem_ok}/20  nodes: {node_ok}/10")
for b in elem_bad[:5]: print("  elem bad:", b)
for b in node_bad[:5]: print("  node bad:", b)
