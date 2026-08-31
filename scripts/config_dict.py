
import sys, json, os
from collections import Counter, defaultdict
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, decode, u32, find_node_section, parse_nodes, find_elem_segments

idx = json.load(open("corpus/corpus_index.json"))
paths = [p["abs"] for p in idx] if isinstance(idx, list) and idx and isinstance(idx[0], dict) else idx
cfg2n = defaultdict(Counter)  # cfg -> {n: count}
cfg_total = Counter()
for pth in paths:
    if not os.path.exists(pth):
        continue
    try:
        m = decode(pth)
    except Exception:
        continue
    for e in m.elements:
        cfg = e.config if hasattr(e, 'config') else (e[1] if isinstance(e, (tuple, list)) else e.get('config'))
        n = len(e.nodes) if hasattr(e, 'nodes') else len(e[2] if isinstance(e, (tuple, list)) else e.get('nodes'))
        cfg2n[cfg][n] += 1
        cfg_total[cfg] += 1
print("config values seen:")
for cfg in sorted(cfg2n):
    cnts = cfg2n[cfg]
    print(f"  config {cfg}: total={cfg_total[cfg]} node-size-dist={dict(sorted(cnts.items()))}")
