import sys, gzip, struct
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
m = D.decode("WS_3.2_3d_tetra_finish.hm")
for eid in (291462, 302867, 291463, 291464, 295000):
    e = m.elements.get(eid)
    print(f"elem {eid}: config={e.config if e else '?'} nodes={e.nodes if e else '?'}")
# find record bytes for 291462
import re
offs = [x for x in range(len(p) - 30) if D.u32(p, x) == 291462]
print("291462 positions:", [hex(o) for o in offs[:3]])
for o in offs[:2]:
    print(f"  @0x{o:x}: {p[o:o+30].hex()}")
    print(f"    flag={D.u16(p, o+12)} refs={[D.u16(p, o+14), D.u16(p, o+18), D.u16(p, o+22), D.u16(p, o+26)]}")
