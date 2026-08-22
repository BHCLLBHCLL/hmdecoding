
import sys, json, os, time
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, decode, d64

idx = json.load(open("corpus/corpus_index.json"))
paths = idx if isinstance(idx, list) else idx.get("files", [])
if isinstance(paths[0], dict):
    paths = [p["abs"] for p in paths]
print("corpus files:", len(paths))
out = []
t0 = time.time()
ok_n = ok_e = total = 0
for pth in paths:
    if not os.path.exists(pth):
        out.append(f"  MISSING {pth}")
        continue
    total += 1
    try:
        m = decode(pth)
        nn = len(m.nodes); ne = len(m.elements)
        mark = "OK" if (nn > 0 and ne > 0) else ("N" if nn > 0 else "X")
        out.append(f"{os.path.basename(pth):42s} | n={nn}/{m.node_count:<8d} e={ne}/{m.elem_count:<8d} v={m.element_variant}")
        if nn == m.node_count and nn > 0:
            ok_n += 1
        if ne == m.elem_count and ne > 0:
            ok_e += 1
    except Exception as ex:
        out.append(f"{os.path.basename(pth):42s} | ERR {ex}")
open("output/ground_truth/sweep_v5.txt", "w", encoding="utf-8").write("\n".join(out))
print(f"files={total} node-full={ok_n} elem-full={ok_e} time={time.time()-t0:.0f}s")
