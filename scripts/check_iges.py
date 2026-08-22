import re, collections
for path in ("output/real_inp/1d_elements_geom.iges", "output/real_inp/ws_geom.iges"):
    data = open(path).read()
    lines = data.splitlines()
    segs = collections.Counter(l[72] if len(l) > 72 else "?" for l in lines)
    params = [l for l in lines if l[72:73] == "P"]
    types = collections.Counter()
    for p in params:
        m = re.match(r"^\s*(\d+)", p)
        if m:
            types[m.group(1)] += 1
    out = f"{path}: {len(lines)} lines, segs={dict(segs)}, types={dict(types)}, tail={lines[-1].strip()}"
    print(out)
