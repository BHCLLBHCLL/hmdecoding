import gzip, struct
def dump_payload(path, label):
    raw = open(path, "rb").read()
    payload = gzip.decompress(raw[12:])
    print("=" * 70)
    print(label, path.split("/")[-1], "payload", len(payload))
    for off in range(0, 0x60, 4):
        v = struct.unpack_from("<I", payload, off)[0]
        d = struct.unpack_from("<d", payload, off)[0]
        print(f"  0x{off:02x}: u32={v:<12} (0x{v:08x})  double={d:.8g}")
    # printable strings
    import re
    strs = sorted(set(re.findall(rb"[ -~]{8,}", payload)), key=len, reverse=True)
    print("  strings:", [s.decode(errors="replace")[:60] for s in strs[:10]])
dump_payload("C:/Program Files/Altair/2019/tutorials/hm/fe_to_surf.hm", "v10-legacy")
dump_payload("C:/Program Files/Altair/2019/tutorials/hm/interfaces/ansys/chapter3.hm.hm", "v12-13")
dump_payload("C:/Program Files/Altair/2019/tutorials/hm/HM-3440/Realizations.hm", "v14+")
dump_payload("C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/dummy_positioner.hm", "v17")
