
import sys, json, os, traceback
sys.path.insert(0, "hmdecoder")
from decoder import decode
gt = json.load(open("output/ground_truth/corpus_gt.json"))
for path, info in gt.items():
    if not os.path.exists(path) or "dummy_positioner" in path or "seat_deformer" in path:
        continue
    try:
        m = decode(path)
    except Exception as ex:
        print("CRASH:", os.path.basename(path), ex)
        break
