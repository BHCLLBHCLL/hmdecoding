
import sys, json, os
sys.path.insert(0, "hmdecoder")
from decoder import decode
gt = json.load(open("output/ground_truth/corpus_gt.json"))
nm = []; em = []; ne_miss = 0; ee_miss = 0; total = 0
for path, info in gt.items():
    if not os.path.exists(path):
        continue
    total += 1
    try:
        m = decode(path)
    except Exception as ex:
        nm.append((os.path.basename(path), "CRASH", 0)); continue
    exp_n = info["counts"]["nodes"]; exp_e = info["counts"]["elements"]
    if exp_n != 0 and len(m.nodes) != exp_n:
        nm.append((os.path.basename(path), len(m.nodes), exp_n))
    if exp_e != 0 and len(m.elements) != exp_e:
        em.append((os.path.basename(path), len(m.elements), exp_e))
print(f"total={total}")
print("\n=== NODE misses (cur, exp) ===")
for x in sorted(nm, key=lambda t: -(t[2] or 0))[:20]:
    print(f"  {x[0]:42s} {x[1]!s:>10s} / {x[2]}")
print("\n=== ELEM misses (cur, exp) ===")
for x in sorted(em, key=lambda t: -(t[2] or 0))[:25]:
    print(f"  {x[0]:42s} {x[1]!s:>10s} / {x[2]}")
print(f"\nnode exact={total-len(nm)}/{total} elem exact={total-len(em)}/{total}")
