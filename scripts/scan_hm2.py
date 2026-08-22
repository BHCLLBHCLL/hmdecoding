import glob, os, re
base = "C:/Program Files/Altair/2019/help/hm"
files = glob.glob(base + "/**/*.htm*", recursive=True)
# Tcl/command 参考
tcl_hits = []
for f in files:
    d = os.path.dirname(f).replace("\\", "/")
    if re.search(r"(tcl|command|api)", d, re.I):
        tcl_hits.append(f)
print("tcl/command/api dirs files:", len(tcl_hits))
for h in tcl_hits[:25]:
    print("  ", h.split("hm/")[-1])
# entities 目录文件
ent = [f for f in files if "/entities/" in f.replace("\\", "/")]
print("entities files:", len(ent))
for e in sorted(ent)[:20]:
    print("  ", e.split("entities/")[-1])
