import glob, os
cands = sorted(glob.glob("C:/Program Files/Altair/2019/tutorials/hm/**/*.hm", recursive=True))
cands += sorted(glob.glob("C:/Program Files/Altair/2019/tutorials/hm/**/*.hm10", recursive=True))
# pick: some tiny, some medium, spread across folders
chosen = [f for f in cands if os.path.getsize(f) < 5000][:6]
chosen += [f for f in cands if f.endswith("spring.hm") or f.endswith("hyperbeam.hm") or f.endswith("leg_geom.hm")]
seen = set()
for f in chosen:
    if f in seen: continue
    seen.add(f)
    data = open(f, "rb").read(112)
    print("=" * 70)
    print(os.path.relpath(f, "C:/Program Files/Altair/2019/tutorials/hm"), "size:", os.path.getsize(f))
    for i in range(0, min(112, len(data)), 16):
        chunk = data[i:i+16]
        hexs = " ".join(f"{b:02x}" for b in chunk)
        ascii_ = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        print(f"{i:04x}  {hexs:<47}  {ascii_}")
