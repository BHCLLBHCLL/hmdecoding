import glob, gzip, struct, os
from collections import Counter
cands = sorted(glob.glob("C:/Program Files/Altair/2019/tutorials/hm/**/*.hm", recursive=True))
cands += sorted(glob.glob("C:/Program Files/Altair/2019/tutorials/hm/**/*.hm10", recursive=True))
PREFIX = struct.pack("<I", 0) + struct.pack("<d", 5.0)   # u32 0 + double 5.0 = 12 bytes
vers = Counter(); u14 = Counter(); u18 = Counter(); u1c = Counter(); n = 0
bad_prefix = []; bad_gz = []
samples = {}
for f in cands:
    raw = open(f, "rb").read()
    if raw[:12] != PREFIX:
        bad_prefix.append(f); continue
    try:
        payload = gzip.decompress(raw[12:])
    except Exception as e:
        bad_gz.append((f, str(e))); continue
    n += 1
    d4 = round(struct.unpack("<d", payload[4:12])[0], 4)
    w14 = struct.unpack("<I", payload[0x14:0x18])[0]
    w18 = struct.unpack("<I", payload[0x18:0x1c])[0]
    w1c = struct.unpack("<I", payload[0x1c:0x20])[0]
    vers[d4] += 1; u14[w14] += 1; u18[w18] += 1; u1c[w1c] += 1
    samples.setdefault(d4, []).append((os.path.getsize(f), len(payload), os.path.basename(f)))
print("total:", len(cands), "standard prefix:", n, "bad prefix:", len(bad_prefix), "gzip fail:", len(bad_gz))
for f in bad_prefix[:5]: print("  bad prefix:", f)
for f, e in bad_gz[:5]: print("  gzip fail:", f, e)
print("double@0x04 distribution:", dict(vers))
print("u32@0x14 distribution:", dict(u14))
print("u32@0x18 distribution:", dict(u18))
print("u32@0x1c distribution:", dict(u1c))
print("samples per DB version:")
for v, items in sorted(samples.items()):
    print(f"  v{v}: {len(items)} files e.g. {items[:2]}")
