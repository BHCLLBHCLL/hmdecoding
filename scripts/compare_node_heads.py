import gzip, struct
def load(path):
    raw = open(path, "rb").read()
    return gzip.decompress(raw[12:])
def u32(off): return struct.unpack_from("<I", p, off)[0]
def d64(off): return struct.unpack_from("<d", p, off)[0]

for name, path, expect in (("1d_elements", "C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", 443),
                           ("bumper", "C:/Program Files/Altair/2019/tutorials/hm/bumper.hm", 473)):
    p = load(path)
    print("=" * 30, name, "payload", len(p))
    # find node-count candidates: [1][136] or count as d64 or count-1
    for i in range(0, len(p) - 16, 4):
        v = u32(i)
        if v == 136:
            for j in range(1, 6):
                if u32(i - j*4) == 1:
                    print(f"  [1..136] @0x{i-4*j:x}")
        if v in (expect, expect - 1, expect + 1):
            print(f"  count {v} @0x{i:x} ctx pre={p[i-16:i].hex()}")
    # d64 count
    import re
    pat = struct.pack("<d", float(expect))
    offs = [m.start() for m in re.finditer(re.escape(pat), p)]
    if offs:
        print(f"  d64 {expect}: {[hex(o) for o in offs[:5]]}")
    # find node-record-like runs: [u32 id][u32 0][u32 0][d64 x] with x plausible, at 52 stride
    # simpler: count [0][0][d64] patterns... skip
    # dump 0xE80..0xF00
    for off in range(0xE80, 0xF00, 16):
        chunk = p[off:off+16]
        hexs = " ".join(f"{b:02x}" for b in chunk)
        ascii_ = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        print(f"  0x{off:04x}  {hexs}  {ascii_}")
