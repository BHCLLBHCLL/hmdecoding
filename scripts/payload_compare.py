import gzip, struct, re
FILES = [
    ("WS_3.2_3d_tetra_finish.hm", "repo sample"),
    ("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "tutorial"),
    ("C:/Program Files/Altair/2019/tutorials/hm/interfaces/madymo/leg_geom.hm", "tiny"),
]
ASCII_TOKEN_RE = re.compile(rb"[A-Za-z0-9_./:-]{4,}")
def u32le(b, off): return struct.unpack_from("<I", b, off)[0]
for path, tag in FILES:
    raw = open(path, "rb").read()
    payload = gzip.decompress(raw[12:])
    print("=" * 72)
    print(tag, path, "compressed", len(raw), "payload", len(payload))
    # head decode
    for off in range(0, 0x40, 4):
        v = u32le(payload, off)
        if off == 4 or off == 12:
            d = struct.unpack_from("<d", payload, off)[0]
            print(f"  off 0x{off:02x}: u32=0x{v:08x}  double={d}")
        else:
            print(f"  off 0x{off:02x}: u32={v} (0x{v:08x})")
    # text records
    print("  text records (tag 0x4000xxxx):")
    n = 0
    for m in re.finditer(rb"[ -~]{6,}", payload):
        s = m.start()
        if s >= 8:
            l1 = u32le(payload, s - 8); l2 = u32le(payload, s - 4)
            if l1 == l2 == len(m.group()):
                tg = u32le(payload, s - 16)
                if tg & 0x40000000:
                    print(f"    @0x{s-16:x} tag=0x{tg:08x} len={l1} text={m.group()[:50]!r}")
                    n += 1
    print(f"    total={n}")
    # named blocks (base/tetras pattern)
    for m in re.finditer(rb"[A-Za-z_][A-Za-z0-9_]{2,31}", payload):
        s = m.start()
        if s >= 12:
            cap = u32le(payload, s - 12); zw = u32le(payload, s - 8); cid = u32le(payload, s - 4)
            if 4 <= cap <= 64 and zw == 0 and 0 < cid <= 64:
                print(f"    named block @0x{s-12:x}: name={m.group().decode()!r} cap={cap} class_id={cid}")
    # tail
    print(f"  tail 32 bytes: {payload[-32:].hex()}")
