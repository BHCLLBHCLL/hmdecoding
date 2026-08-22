
import sys, json, os
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, decode, d64

gt = json.load(open("output/ground_truth/corpus_gt.json"))
# structure?
if isinstance(gt, dict):
    k0 = list(gt.keys())[:3]
    print("gt keys sample:", k0)
    print("gt sample:", json.dumps(gt[k0[0]])[:300] if isinstance(gt[k0[0]], (dict, list)) else gt[k0[0]])
