import gzip, struct, re
def u32(p, o): return struct.unpack_from("<I", p, o)[0]
def named_blocks(payload):
    blocks = []
    for m in re.finditer(rb"[A-Za-z_][A-Za-z0-9_]{1,31}", payload):
        s = m.start()
        if s < 12:
            continue
        cap = u32(payload, s - 12)
        zw = u32(payload, s - 8)
        cid = u32(payload, s - 4)
        if 4 <= cap <= 64 and zw == 0 and 0 < cid <= 64:
            blocks.append((s - 12, m.group().decode("ascii", "replace"), cid, cap))
    return blocks
raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])
blocks = named_blocks(p)
print("blocks:", len(blocks))
for b in blocks[:40]:
    print(f"  @0x{b[0]:x} name={b[1]!r} cid={b[2]} cap={b[3]}")
