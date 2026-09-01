#!/usr/bin/env python3
"""auto_compare.py — 全语料 oracle 对照回归门禁.

decode 全语料 vs corpus_gt.json (oracle 计数), 输出覆盖率报告.
退出码: 0 = 无回归 (node/elem exact 不低于历史快照), 1 = 有回归.
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "hmdecoder"))
from decoder import decode

# 历史快照 (达标基线; 低于此视为回归)
SNAPSHOT = {"node": 116, "elem": 119, "total": 123}

def main():
    gt = json.load(open(os.path.join(os.path.dirname(__file__), "..",
                     "output", "ground_truth", "corpus_gt.json")))
    n_ok = e_ok = total = 0
    misses = []
    for path, info in gt.items():
        if not os.path.exists(path):
            continue
        total += 1
        try:
            m = decode(path)
        except Exception as ex:
            misses.append((os.path.basename(path), "CRASH", 0, 0))
            continue
        exp_n = info["counts"]["nodes"]; exp_e = info["counts"]["elements"]
        if exp_n == 0 or len(m.nodes) == exp_n:
            n_ok += 1
        else:
            misses.append((os.path.basename(path), "node", len(m.nodes), exp_n))
        if exp_e == 0 or len(m.elements) == exp_e:
            e_ok += 1
        else:
            misses.append((os.path.basename(path), "elem", len(m.elements), exp_e))
    print(f"total={total} node-ok={n_ok} elem-ok={e_ok}")
    print(f"node-exact {n_ok}/{total} (snapshot {SNAPSHOT['node']})")
    print(f"elem-exact {e_ok}/{total} (snapshot {SNAPSHOT['elem']})")
    for mn in misses:
        print("  X", mn)
    ok = n_ok >= SNAPSHOT["node"] and e_ok >= SNAPSHOT["elem"]
    print("PASS" if ok else "REGRESSION")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
