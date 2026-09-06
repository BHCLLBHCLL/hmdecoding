#!/usr/bin/env python3
"""M4 几何段字节级定位: 用 oracle 点坐标在 payload 中定位几何点段.

策略 (由弱到强):
  A. 精确三连搜索: 把 oracle 点 (x,y,z) pack 成 24 字节, 在 payload 中 find.
     命中即证明该区域按 [x][y][z] 连续 double 存储.
  B. 容差三连扫描: 若 oracle 文本精度不足导致 A 失败, 逐 8 字节对齐解析
     (d,d,d) 与 oracle 点集比对 (容差可配), 命中位置聚类.

命中簇的步长直方图用于推断记录步长 (点记录 = 坐标 + id + 附加字段).

用法: python scripts/m4_locate_geom.py <file.hm> [--tol 1e-6] [--n 20]
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


def _norm(s):
    return os.path.normcase(os.path.normpath(s.replace("\\", "/")))


def oracle_points(path, gt):
    want = _norm(path)
    for k, v in gt.items():
        if _norm(k) == want:
            return {int(i): c for i, c in v.get("points", {}).items()}
    return {}


def exact_triples(p, op, n=20, cap=400):
    """策略 A: 精确 24 字节三连搜索."""
    hits = []
    for pid in sorted(op)[:n]:
        x, y, z = op[pid]
        pat = struct.pack("<ddd", x, y, z)
        start = 0
        cnt = 0
        while cnt < 8:
            i = p.find(pat, start)
            if i < 0:
                break
            hits.append((pid, i))
            start = i + 1
            cnt += 1
        if len(hits) > cap:
            break
    return hits


def tol_triples(p, op, tol=1e-6, cap=4000):
    """策略 B: 容差三连扫描 (8 字节对齐)."""
    pool = [(pid, xyz) for pid, xyz in op.items()]
    hits = []
    n = len(p) - 24
    for off in range(0, n + 1, 8):
        x, y, z = struct.unpack_from("<ddd", p, off)
        if abs(x) > 1e9 or abs(y) > 1e9 or abs(z) > 1e9:
            continue
        for pid, c in pool:
            if (abs(x - c[0]) < tol and abs(y - c[1]) < tol and abs(z - c[2]) < tol):
                hits.append((pid, off))
                break
        if len(hits) > cap:
            break
    return hits


def step_hist(offs):
    s = {}
    for a, b in zip(offs, offs[1:]):
        s[b - a] = s.get(b - a, 0) + 1
    return sorted(s.items(), key=lambda kv: -kv[1])[:8]


def dump(p, base, rows=8):
    for row in range(rows):
        o = base + row * 16
        if o < 0 or o + 16 > len(p):
            break
        chunk = p[o:o + 16]
        hexs = " ".join(f"{b:02x}" for b in chunk)
        d0, d1 = struct.unpack_from("<dd", p, o)
        u0, u1 = struct.unpack_from("<II", p, o)
        print(f"    {o:8d}  {hexs} | {d0:>13.6g} {d1:>13.6g} | u32={u0},{u1}")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    tol = 1e-6
    n = 20
    if "--tol" in sys.argv:
        tol = float(sys.argv[sys.argv.index("--tol") + 1])
    if "--n" in sys.argv:
        n = int(sys.argv[sys.argv.index("--n") + 1])
    if not args:
        print("usage: m4_locate_geom.py <file.hm>")
        sys.exit(1)
    path = args[0]
    gt = json.loads(GT.read_text(encoding="utf-8")) if GT.exists() else {}
    op = oracle_points(path, gt)
    if not op:
        print(f"no oracle points for {path}")
        sys.exit(1)
    p = load_payload(path)
    print(f"file={Path(path).name} payload={len(p)} oracle_points={len(op)}")

    hits = exact_triples(p, op, n=n)
    print(f"[A] exact triples: {len(hits)} hits")
    if not hits:
        hits = tol_triples(p, op, tol=tol)
        print(f"[B] tolerance triples: {len(hits)} hits")
    if not hits:
        print("no hits")
        return
    offs = sorted(o for _, o in hits)
    print(f"offset range: [{offs[0]}, {offs[-1]}]")
    print(f"step histogram (all): {step_hist(offs)}")
    # 取最密集的一段
    print("\nfirst 10 hits (pid, off):", hits[:10])
    base = offs[0]
    print(f"\nhexdump @ {base - 16}:")
    dump(p, base - 16, rows=10)
    # 若步长规整, 打印连续 3 条记录
    st = step_hist(offs)
    if st and st[0][1] >= 3:
        step = st[0][0]
        print(f"\nconsecutive records @ step={step}:")
        dump(p, base, rows=4 * step // 16 + 2)


if __name__ == "__main__":
    main()
