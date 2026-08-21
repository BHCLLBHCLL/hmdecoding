import sys
sys.path.insert(0, ".")
from hmdecoder import decode
m = decode("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm")
gt = {}
for line in open("output/ground_truth/elem_all.log", encoding="utf-8").read().splitlines()[1:]:
    parts = line.split()
    if len(parts) == 5:
        gt[int(parts[0])] = tuple(int(x) for x in parts[1:5])
for eid, quad in gt.items():
    e = m.elements.get(eid)
    if not e or tuple(e.nodes) != quad:
        print(f"elem {eid}: decoded={e.nodes if e else None} gt={quad}")
