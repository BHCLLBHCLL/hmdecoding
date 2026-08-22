import glob, re, collections, os
base = "C:/Program Files/Altair/2019/hm/scripts"
files = glob.glob(base + "/**/*.tcl", recursive=True)
print("tcl files:", len(files))
star_cmds = collections.Counter()
hm_funcs = collections.Counter()
ascii_hits = []
for f in files:
    try:
        data = open(f, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue
    for m in re.finditer(r"\*(\w+)", data):
        star_cmds[m.group(1)] += 1
    for m in re.finditer(r"\bhm_(\w+)", data):
        hm_funcs[m.group(1)] += 1
    if re.search(r"hmascii|ascii\s*\.?hm", data, re.I):
        ascii_hits.append(f)
out = []
out.append("Top * commands:")
for c, n in star_cmds.most_common(40):
    out.append(f"  *{c}: {n}")
out.append("Top hm_ functions:")
for c, n in hm_funcs.most_common(30):
    out.append(f"  hm_{c}: {n}")
out.append(f"hmascii related files: {len(ascii_hits)}")
for h in ascii_hits[:10]:
    out.append("  " + h.split("scripts/")[-1])
open("output/ground_truth/tcl_usage.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
