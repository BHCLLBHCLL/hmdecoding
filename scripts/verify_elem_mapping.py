import gzip, struct, re

raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(off): return struct.unpack_from("<I", p, off)[0]

c = struct.pack("<I", 0x70241FF5)
offs = [m.start() for m in re.finditer(re.escape(c), p)]
# data records: those with +0x24 in 1..400
recs = {}
for o in offs:
    s = o - 0x20
    idx = u32(s + 0x24)
    if 1 <= idx <= 400:
        recs[idx] = s
print("data records:", len(recs))
GT = {198: (294,292,291,293), 199: (220,282,294,221), 200: (282,281,292,294),
      201: (317,322,304,305), 202: (322,69,70,304), 203: (318,321,322,317), 204: (321,68,69,322)}
for eid, (n1,n2,n3,n4) in GT.items():
    s = recs.get(eid)
    if s is None:
        print(f"elem {eid}: record NOT FOUND"); continue
    got = (u32(s+8), u32(s+0xc), u32(s+0x10), u32(s+0x14))
    match = "MATCH" if got == (n1,n2,n3,n4) else "MISMATCH"
    print(f"elem {eid} @0x{s:x}: got {got} expected ({n1},{n2},{n3},{n4}) {match}")
# also check elem 1..5
print("first 5 records:")
for eid in range(1, 6):
    s = recs[eid]
    print(f"  elem {eid} @0x{s:x}: [{u32(s+0)} {u32(s+4)} {u32(s+8)} {u32(s+0xc)} {u32(s+0x10)} {u32(s+0x14)} {u32(s+0x18)} {u32(s+0x1c)} {u32(s+0x20):#x} {u32(s+0x24)} {u32(s+0x28):#x} {u32(s+0x2c)}]")
