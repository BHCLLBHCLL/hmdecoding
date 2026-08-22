
import sys, json, os
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, decode, d64

gt = json.load(open("output/ground_truth/corpus_gt.json"))
n_ok = e_ok = total = 0
miss_n = miss_e = []
for path, info in gt.items():
    if not os.path.exists(path):
        continue
    total += 1
    m = decode(path)
    exp_n = info["counts"]["nodes"]
    exp_e = info["counts"]["elements"]
    got_n = len(m.nodes); got_e = len(m.elements)
    if exp_n == 0 or got_n == exp_n:
        n_ok += 1
    else:
        miss_n.append((os.path.basename(path), got_n, exp_n))
    if exp_e == 0 or got_e == exp_e:
        e_ok += 1
    else:
        miss_e.append((os.path.basename(path), got_e, exp_e))
print(f"total={total} node-ok={n_ok} elem-ok={e_ok}")
print("\nNODE misses (got, exp):")
for x in sorted(miss_n, key=lambda t: -t[2])[:25]:
    print(f"  {x[0]:42s} {x[1]:>8d} / {x[2]:>8d}")
print("\nELEM misses (got, exp):")
for x in sorted(miss_e, key=lambda t: -t[2])[:25]:
    print(f"  {x[0]:42s} {x[1]:>8d} / {x[2]:>8d}")
