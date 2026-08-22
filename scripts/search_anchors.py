
import sys, json, os
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32

gt = json.load(open("output/ground_truth/multi_elem_gt.json"))
for fname, info in gt.items():
    path = f"C:/Program Files/Altair/2019/tutorials/hm/{fname}"
    if not os.path.exists(path):
        path = f"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/{fname}"
    p = load_payload(path)
    print(f"== {fname} len={len(p)}")
    for eid, d in info["elems"].items():
        nds = [x for x in d["nodes"] if x]
        if len(nds) < 2: continue
        hits = []
        for i in range(0, len(p) - 4 * len(nds)):
            if all(u32(p, i + j * 4) == nds[j] for j in range(len(nds))):
                hits.append(i)
        if hits:
            print(f"   E{eid} cfg={d['cfg']} nds={nds} hits={hits[:8]}")
