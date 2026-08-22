import sys
print("start", flush=True)
sys.path.insert(0, ".")
import json
gt = json.load(open("output/ground_truth/corpus_gt.json", encoding="utf-8"))
print("gt loaded:", len(gt), flush=True)
from hmdecoder import decode
print("decoder imported", flush=True)
paths = [p for p, d in gt.items() if d.get("counts", {}).get("nodes", 0) > 0]
print("files with nodes:", len(paths), flush=True)
for path in paths[:3]:
    m = decode(path)
    print(" ", path.split("\\")[-1], len(m.nodes), len(m.elements), flush=True)
