
import sys, json, os
sys.path.insert(0, "hmdecoder")
from decoder import decode
gt = json.load(open("output/ground_truth/corpus_gt.json"))
misses = []
for path, info in gt.items():
    if not os.path.exists(path) or "dummy_positioner" in path or "seat_deformer" in path:
        continue
    m = decode(path)
    exp_e = info["counts"]["elements"]
    if exp_e != 0 and len(m.elements) != exp_e:
        misses.append((os.path.basename(path), len(m.elements), exp_e))
for x in sorted(misses, key=lambda t: -t[2])[:12]:
    print(f"  {x[0]:42s} {x[1]:>8d} / {x[2]:>8d}")
print("total elem misses:", len(misses))
