import gzip, struct, re

raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(off): return struct.unpack_from("<I", p, off)[0]

GT = {198: (294,292,291,293), 199: (220,282,294,221), 200: (282,281,292,294),
      201: (317,322,304,305), 202: (322,69,70,304), 203: (318,321,322,317), 204: (321,68,69,322)}
for eid, quad in GT.items():
    pat = struct.pack("<4I", *quad)
    hits = [m.start() for m in re.finditer(re.escape(pat), p)]
    print(f"elem {eid} GT {quad}: hits at {[hex(h) for h in hits]}")
    for h in hits:
        print(f"    @0x{h:x} pre={p[h-16:h].hex()}")
