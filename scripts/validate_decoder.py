import sys
sys.path.insert(0, ".")
from hmdecoder import decode
m = decode("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm")
gt = {}
for line in open("output/ground_truth/elem_all.log", encoding="utf-8").read().splitlines()[1:]:
    parts = line.split()
    if len(parts) == 5:
        gt[int(parts[0])] = tuple(int(x) for x in parts[1:5])
bad = 0
for eid, quad in gt.items():
    e = m.elements.get(eid)
    if not e or tuple(e.nodes) != quad:
        bad += 1
print("elements verified:", len(gt) - bad, "/", len(gt))
# node coords
nc = {}
for line in open("output/ground_truth/node_many.log", encoding="utf-8").read().splitlines():
    parts = line.split()
    if len(parts) == 4:
        nc[int(parts[0])] = tuple(float(x) for x in parts[1:4])
badn = 0
for nid, (x, y, z) in nc.items():
    n = m.nodes.get(nid)
    if not n or abs(n.x - x) > 1e-6 or abs(n.y - y) > 1e-6 or abs(n.z - z) > 1e-6:
        badn += 1
print("nodes verified:", len(nc) - badn, "/", len(nc))
