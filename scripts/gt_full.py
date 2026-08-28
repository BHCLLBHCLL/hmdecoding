
import sys, json, os
sys.path.insert(0, "hmdecoder")
from decoder import decode
gt = json.load(open("output/ground_truth/corpus_gt.json"))
n_ok = e_ok = total = 0
for path, info in gt.items():
    if not os.path.exists(path):
        continue
    total += 1
    m = decode(path)
    exp_n = info["counts"]["nodes"]; exp_e = info["counts"]["elements"]
    if exp_n == 0 or len(m.nodes) == exp_n:
        n_ok += 1
    if exp_e == 0 or len(m.elements) == exp_e:
        e_ok += 1
print(f"ALL: total={total} node-ok={n_ok} elem-ok={e_ok}")
