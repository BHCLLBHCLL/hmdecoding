import sys
sys.path.insert(0, ".")
from hmdecoder import decode
m = decode("WS_3.2_3d_tetra_finish.hm")
f460 = [eid for eid, e in m.elements.items() if e.config == 204]
f359 = [eid for eid, e in m.elements.items() if e.config == 103]
print("config204:", len(f460), "config103:", len(f359))
print("sample 204:", f460[:3], "sample 103:", f359[:3])
