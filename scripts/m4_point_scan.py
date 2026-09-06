#!/usr/bin/env python3
"""M4 几何点段通用扫描: 不依赖段头签名的点记录链检测.

段头签名 (0x8120/256) 只覆盖部分 db 版本 (如 lsdyna 11.05), 其它版本段头标记
不同 (Full_Motion 等出现错位变体). 因此改用两条通用判据定位点段:

  1. 步长链式: 真实点段以固定步长 (48/52/56) 连续排布, 随机数据难以连续 N 条命中
  2. 空间连续: 同一几何实体的点空间聚集, 相邻点距离远小于孤立随机三元组

用法: python scripts/m4_point_scan.py <file.hm> [--min 6]
"""
import os
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from hmdecoder.decoder import load_payload  # noqa: E402

LIM = 1e7
STEPS = (48, 52, 56)


def _ok(x, y, z):
    if not (abs(x) < LIM and abs(y) < LIM and abs(z) < LIM):
        return False
    # 排除零填充区与 denormal 垃圾值: payload 中大片 0x00 / 极小浮点数
    # 会被误判为合法坐标并形成超长假链
    ax, ay, az = abs(x), abs(y), abs(z)
    if max(ax, ay, az) < 1e-9:
        return False
    for v in (ax, ay, az):
        if 0 < v < 1e-260:
            return False
    return True


def candidates(p):
    """预筛: 合理坐标三元组位置集合."""
    cand = set()
    n = len(p) - 24
    for off in range(0, n + 1):
        x, y, z = struct.unpack_from("<ddd", p, off)
        if _ok(x, y, z):
            cand.add(off)
    return cand


def chains(cand, p, step, min_len=6, max_gap_ratio=0.5):
    """在候选中找步长==step 的链, 并要求空间连续 (相邻距离不超过段内典型尺度)."""
    out = []
    used = set()
    for o in sorted(cand):
        if o in used:
            continue
        # 前向延伸
        seq = [o]
        cur = o
        while cur + step in cand and (cur + step) not in used:
            cur += step
            seq.append(cur)
        if len(seq) < min_len:
            continue
        # 空间连续性校验: 相邻点距离的中位数应远小于整体包围盒
        pts = [struct.unpack_from("<ddd", p, s) for s in seq]
        dists = []
        for a, b in zip(pts, pts[1:]):
            dists.append(((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5)
        dists.sort()
        med = dists[len(dists) // 2]
        xs = [q[0] for q in pts]
        ys = [q[1] for q in pts]
        zs = [q[2] for q in pts]
        diag = ((max(xs) - min(xs)) ** 2 + (max(ys) - min(ys)) ** 2
                + (max(zs) - min(zs)) ** 2) ** 0.5
        if diag <= 0 or med > diag * max_gap_ratio:
            continue
        out.append((seq[0], step, pts))
        used.update(seq)
    return out


def scan_segments(p, min_len=6):
    cand = candidates(p)
    res = []
    for s in STEPS:
        res.extend(chains(cand, p, s, min_len=min_len))
    res.sort(key=lambda r: -len(r[2]))
    return res


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    min_len = 6
    if "--min" in sys.argv:
        min_len = int(sys.argv[sys.argv.index("--min") + 1])
    if not args:
        print("usage: m4_point_scan.py <file.hm>")
        sys.exit(1)
    p = load_payload(args[0])
    segs = scan_segments(p, min_len=min_len)
    print(f"file={Path(args[0]).name} payload={len(p)} segments={len(segs)} "
          f"points={sum(len(s[2]) for s in segs)}")
    for base, step, pts in segs[:8]:
        xs = [q[0] for q in pts]
        print(f"  seg@{base:<9d} step={step} n={len(pts):<4d} "
              f"x=[{min(xs):.3g}, {max(xs):.3g}]")


if __name__ == "__main__":
    main()
