#!/usr/bin/env python3
"""M4 几何点段定位: 用 oracle 点坐标做三元组容差扫描, 定位点段结构与范围.

关键前提 (实测):
  .hm 以 float64 存储几何坐标, 但 hm_getvalue 以 float32 精度返回
  -> oracle 值与存储值的相对误差约 1e-7~1e-5, 必须用「相对容差」匹配,
     此前用 1e-6 绝对容差搜索导致 0 命中.

方法:
  1. 把 oracle 所有坐标分量量化成 6 位有效数字集合 (快速判重)
  2. 逐字节扫描 payload, 解析 double; 命中集合则记为候选
  3. 候选位置验证三元组 (x,y,z) 是否同时匹配某一个 oracle 点
  4. 命中位置聚类 -> 点段候选区; 步长直方图 -> 记录步长

用法: python scripts/m4_point_segment.py "<path.hm>"
"""
import json
import os
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from hmdecoder.decoder import load_payload  # noqa: E402

GT = ROOT / "output" / "ground_truth" / "m4_geom_gt.json"
REL = 1e-5  # 相对容差 (覆盖 float32 返回精度误差)


def _norm(s):
    return os.path.normcase(os.path.normpath(s.replace("\\", "/")))


def oracle_rec(path):
    gt = json.loads(GT.read_text(encoding="utf-8"))
    want = _norm(path)
    for k, v in gt.items():
        if _norm(k) == want:
            return {int(i): c for i, c in v["points"].items()}
    return {}


def scan(p, op):
    """逐字节扫描, 返回 [(pid, off)]: 该位置起的 (x,y,z) 与 oracle 点 pid 匹配."""
    comps = set()
    for xyz in op.values():
        for v in xyz:
            comps.add(float("%.6g" % v))
    by_first = {}
    for pid, (x, y, z) in op.items():
        by_first.setdefault(float("%.6g" % x), []).append((pid, y, z))

    hits = []
    n = len(p) - 24
    for off in range(0, n + 1):
        v0 = struct.unpack_from("<d", p, off)[0]
        q = float("%.6g" % v0)
        if q not in comps:
            continue
        cands = by_first.get(q)
        if not cands:
            continue
        v1 = struct.unpack_from("<d", p, off + 8)[0]
        v2 = struct.unpack_from("<d", p, off + 16)[0]
        for pid, y, z in cands:
            if (abs(v1 - y) <= REL * max(1.0, abs(y))
                    and abs(v2 - z) <= REL * max(1.0, abs(z))):
                hits.append((pid, off))
                break
    return hits


def main():
    if len(sys.argv) < 2:
        print("usage: m4_point_segment.py <file.hm>")
        sys.exit(1)
    path = sys.argv[1]
    op = oracle_rec(path)
    if not op:
        print("no oracle points for", path)
        sys.exit(1)
    p = load_payload(path)
    print(f"file={Path(path).name} payload={len(p)} oracle_points={len(op)}")
    hits = scan(p, op)
    print(f"triple hits: {len(hits)}  (unique pids: {len(set(i for i, _ in hits))})")
    if not hits:
        return
    offs = sorted(o for _, o in hits)
    # 聚类
    clusters = []
    cur = [offs[0]]
    for o in offs[1:]:
        if o - cur[-1] <= 4096:
            cur.append(o)
        else:
            clusters.append(cur)
            cur = [o]
    clusters.append(cur)
    clusters.sort(key=len, reverse=True)
    print(f"clusters: {len(clusters)}  top sizes: {[len(c) for c in clusters[:6]]}")
    for i, c in enumerate(clusters[:3]):
        steps = {}
        for a, b in zip(c, c[1:]):
            steps[b - a] = steps.get(b - a, 0) + 1
        top = sorted(steps.items(), key=lambda kv: -kv[1])[:5]
        print(f"\n cluster#{i}: n={len(c)} range=[{c[0]}, {c[-1]}] span={c[-1] - c[0]}")
        print(f"   step hist: {top}")
        print(f"   first offsets: {c[:8]}")
        # 打印首记录结构
        base = c[0]
        print(f"   record dump @ {base}:")
        for r in range(0, 64, 4):
            o = base + r
            if o + 4 > len(p):
                break
            u, = struct.unpack_from("<I", p, o)
            d, = struct.unpack_from("<d", p, o)
            print(f"     +{r:2d} @{o:7d} {p[o:o + 4].hex()}  u32={u:<11d} d64={d!r}")


if __name__ == "__main__":
    main()
