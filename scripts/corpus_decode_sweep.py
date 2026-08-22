import sys, json, gzip, struct
sys.path.insert(0, ".")
from hmdecoder import decode
gt = json.load(open("output/ground_truth/corpus_gt.json", encoding="utf-8"))
results = []
for path, data in gt.items():
    if data.get("counts", {}).get("nodes", 0) == 0:
        continue
    try:
        m = decode(path)
    except Exception as e:
        results.append((path.split("\\")[-1], "ERR", str(e)[:40]))
        continue
    nn = data["counts"]["nodes"]
    ne = data["counts"]["elements"]
    ok_n = "OK" if len(m.nodes) == nn else f"X({len(m.nodes)}/{nn})"
    ok_e = "OK" if len(m.elements) == ne else f"X({len(m.elements)}/{ne})"
    results.append((path.split("\\")[-1], ok_n, ok_e, round(m.db_version, 2)))
for r in results[:40]:
    print("  ", r)
print("total:", len(results))
