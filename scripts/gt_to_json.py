
import json, re
txt = open("output/ground_truth/multi_elem.txt", encoding="utf-8").read()
data = {}
cur = None
for ln in txt.splitlines():
    if ln.startswith("===== "):
        cur = ln[6:].strip()
        data[cur] = {"count": None, "first8": [], "elems": {}}
    elif cur and ln.startswith("  count="):
        parts = ln.split("first8=")
        data[cur]["count"] = int(parts[0].replace("  count=", "").strip())
        data[cur]["first8"] = [int(x) for x in parts[1].split()]
    elif cur and ln.startswith("  E "):
        m = re.match(r"  E (\d+) cfg=(\d+) nodes=(.*)", ln)
        data[cur]["elems"][int(m.group(1))] = {"cfg": int(m.group(2)),
                                               "nodes": [int(x) for x in m.group(3).split() if x]}
json.dump(data, open("output/ground_truth/multi_elem_gt.json", "w"), indent=1)
for k, v in data.items():
    print(f"{k}: count={v['count']} first8={v['first8'][:4]}")
