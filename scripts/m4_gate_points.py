#!/usr/bin/env python3
"""M4.1 门禁: 几何点解码 vs oracle 真值覆盖率 (全语料).

对照口径: .hm 以 float64 存几何坐标, 而 hm_getvalue 以 float32 精度返回,
故必须用「相对容差」(默认 1e-5) 匹配, 绝对容差会导致大面积误判.

用法: python scripts/m4_gate_points.py [--limit N] [--rel 1e-5]
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from hmdecoder.decoder import load_payload  # noqa: E402
from m4_point_segment import oracle_rec  # noqa: E402
from m4_point_scan import scan_segments  # noqa: E402

GT = ROOT / "output" / "ground_truth" / "m4_geom_gt.json"


def match(op, pts, rel=1e-5):
    """返回 (matched_pid 集合, 未匹配数)."""
    got = set()
    for (x, y, z) in pts:
        for pid, c in op.items():
            if pid in got:
                continue
            if (abs(x - c[0]) <= rel * max(1.0, abs(c[0]))
                    and abs(y - c[1]) <= rel * max(1.0, abs(c[1]))
                    and abs(z - c[2]) <= rel * max(1.0, abs(c[2]))):
                got.add(pid)
                break
    return got


def main():
    rel = 1e-5
    limit = None
    if "--rel" in sys.argv:
        rel = float(sys.argv[sys.argv.index("--rel") + 1])
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    gt = json.loads(GT.read_text(encoding="utf-8"))
    rows = []
    for k, v in gt.items():
        n = len(v.get("points", {}))
        if n:
            rows.append((n, k))
    rows.sort(reverse=True)
    if limit:
        rows = rows[:limit]
    print(f"{'file':40s} {'oracle':>7} {'decoded':>8} {'match':>6} {'ratio':>7}")
    tot_o = tot_m = 0
    done = 0
    for n, path in rows:
        op = oracle_rec(path)
        if not op:
            continue
        try:
            p = load_payload(path)
            segs = scan_segments(p, min_len=4)
            pts = []
            for _, _, recs in segs:
                pts.extend(recs)
            got = match(op, pts, rel)
        except Exception as e:  # noqa: BLE001
            print(f"{os.path.basename(path)[:39]:40s} ERROR {e!r}")
            continue
        done += 1
        tot_o += len(op)
        tot_m += len(got)
        print(f"{os.path.basename(path.replace(chr(92), '/'))[:39]:40s} {len(op):>7} "
              f"{len(pts):>8} {len(got):>6} {len(got) / max(1, len(op)):>7.3f}")
    print(f"\nfiles={done}  oracle_points={tot_o}  matched={tot_m}  "
          f"coverage={tot_m / max(1, tot_o):.3f}")


if __name__ == "__main__":
    main()
