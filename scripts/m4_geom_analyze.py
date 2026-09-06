#!/usr/bin/env python3
"""M4 几何段分析: 现有解码 (geo_points/display_points) vs oracle 几何真值对照.

用法: python scripts/m4_geom_analyze.py [file.hm ...]
     不带参数则取 m4_geom_gt.json 中已采集的前若干文件.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from hmdecoder.decoder import decode  # noqa: E402

GT_JSON = ROOT / "output" / "ground_truth" / "m4_geom_gt.json"
LOG = ROOT / "output" / "ground_truth" / "m4_geom_oracle.log"


def load_gt():
    if GT_JSON.exists():
        return json.loads(GT_JSON.read_text(encoding="utf-8"))
    return {}


def compare(path):
    m = decode(path)
    gt = load_gt().get(path, {})
    if not gt:
        return {"path": path, "err": "no oracle"}
    op = {int(k): v for k, v in gt.get("points", {}).items()}
    ol = {int(k): v for k, v in gt.get("lines", {}).items()}
    os_ = {int(k): v for k, v in gt.get("surfaces", {}).items()}
    oso = {int(k): v for k, v in gt.get("solids", {}).items()}

    gp = m.geo_points
    dp = m.display_points
    # 坐标容差匹配
    def match_count(cand, tol=1e-6):
        """候选点集 (id->[x,y,z]) 中, 能匹配上 oracle 坐标的数量."""
        got = {}
        for opid, xyz in op.items():
            for cid, node in cand.items():
                if (abs(node.x - xyz[0]) < tol and abs(node.y - xyz[1]) < tol
                        and abs(node.z - xyz[2]) < tol):
                    got[opid] = cid
                    break
        return got

    gp_m = match_count(gp)
    dp_m = match_count(dp)
    both = dict(gp)
    both.update(dp)
    both_m = match_count(both)
    return {
        "path": path,
        "name": os.path.basename(path.replace("\\", "/")),
        "db": m.db_version,
        "oracle": {"points": len(op), "lines": len(ol), "surfaces": len(os_),
                   "solids": len(oso)},
        "geo_points": len(gp), "display_points": len(dp), "nodes": len(m.nodes),
        "match": {"geo": len(gp_m), "disp": len(dp_m), "both": len(both_m)},
        "match_ratio": round(len(both_m) / len(op), 3) if op else 0.0,
    }


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        gt = load_gt()
        if not gt:
            print("no oracle data; run: python scripts/m4_geom_oracle.py parse")
            sys.exit(1)
        args = sorted(gt, key=lambda p: -(
            len(gt[p]["points"]) + len(gt[p]["lines"])))[:6]
    rows = []
    for p in args:
        try:
            rows.append(compare(p))
        except Exception as e:  # noqa: BLE001
            rows.append({"path": p, "err": repr(e)})
    print(f"{'file':38s} {'db':>6} | {'oPts':>5} {'oLns':>5} {'oSrf':>5} {'oSol':>4} "
          f"| {'geo':>5} {'disp':>5} | {'match':>6} {'ratio':>6}")
    for r in rows:
        if "err" in r:
            print(f"{r['path'][:37]:38s} ERR {r['err']}")
            continue
        o = r["oracle"]
        print(f"{r['name'][:37]:38s} {r['db']:>6.2f} | {o['points']:>5} {o['lines']:>5} "
              f"{o['surfaces']:>5} {o['solids']:>4} | {r['geo_points']:>5} "
              f"{r['display_points']:>5} | {r['match']['both']:>6} "
              f"{r['match_ratio']:>6.3f}")
