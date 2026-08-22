import sys, json, traceback
sys.path.insert(0, ".")
from hmdecoder import decode
gt = json.load(open("output/ground_truth/corpus_gt.json", encoding="utf-8"))
out = []
ok_n = ok_e = 0
nfiles = 0
for path, data in gt.items():
    nn = data.get("counts", {}).get("nodes", 0)
    if nn == 0:
        continue
    nfiles += 1
    try:
        m = decode(path)
    except Exception:
        out.append((path.split("/")[-1], "ERR", traceback.format_exc()[:100]))
        continue
    ne = data.get("counts", {}).get("elements", 0)
    s_n = "OK" if len(m.nodes) == nn else f"X({len(m.nodes)}/{nn})"
    s_e = "OK" if len(m.elements) == ne else f"X({len(m.elements)}/{ne})"
    if s_n == "OK": ok_n += 1
    if s_e == "OK": ok_e += 1
    out.append((path.split("/")[-1], s_n, s_e, m.element_variant))
with open("output/ground_truth/sweep_results.txt", "w", encoding="utf-8") as f:
    for r in out:
        f.write("  " + " | ".join(str(x) for x in r) + "\n")
    f.write(f"node-OK: {ok_n}/{nfiles}  elem-OK: {ok_e}/{nfiles}\n")
print("done", nfiles)
