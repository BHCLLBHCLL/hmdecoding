#!/usr/bin/env python3
"""M4 几何 oracle 采集驱动 + 日志解析.

用法:
  python scripts/m4_geom_oracle.py harvest [--limit N]   # 采集含几何的语料文件
  python scripts/m4_geom_oracle.py parse                 # 解析日志 -> JSON
  python scripts/m4_geom_oracle.py stats                 # 统计门禁
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HM = r"C:/Program Files/Altair/2019/hm/bin/win64/hmbatch.exe"
TCL = ROOT / "scripts" / "m4_geom_oracle.tcl"
GT = ROOT / "output" / "ground_truth" / "corpus_gt.json"
LOG = ROOT / "output" / "ground_truth" / "m4_geom_oracle.log"
OUT = ROOT / "output" / "ground_truth" / "m4_geom_gt.json"
BATCH = 6  # 每次 hmbatch 会话处理的文件数


def geom_files():
    """返回语料中含几何实体 (lines/surfaces/solids 任一 > 0) 的文件路径, 小模型优先."""
    gt = json.loads(GT.read_text(encoding="utf-8"))
    rows = []
    for path, rec in gt.items():
        c = rec.get("counts", {})
        n = (c.get("lines", 0) or 0) + (c.get("surfaces", 0) or 0) + (c.get("solids", 0) or 0)
        if n > 0:
            rows.append((n, path))
    # 降序: 几何规模大的模型信息量高, 优先采集
    rows.sort(reverse=True)
    return [p for _, p in rows]


def harvest(limit=None, batch=BATCH):
    files = geom_files()
    if limit:
        files = files[:limit]
    done = set()
    if LOG.exists():
        done = set(re.findall(r"^==FILE== (.+)$", LOG.read_text(encoding="utf-8", errors="replace"),
                              re.M))
    todo = [f for f in files if f not in done]
    print(f"total={len(files)} done={len(done)} todo={len(todo)}")
    for i in range(0, len(todo), batch):
        chunk = todo[i:i + batch]
        (ROOT / "output" / "m4_geom_files.txt").write_text("\n".join(chunk), encoding="utf-8")
        try:
            r = subprocess.run([HM, "-tcl", str(TCL)], capture_output=True, text=True,
                               timeout=3600, cwd=str(ROOT))
            rc = r.returncode
        except subprocess.TimeoutExpired:
            rc = "TIMEOUT"
        print(f"batch {i // batch + 1}: {[os.path.basename(x) for x in chunk]} rc={rc}")
    return todo


RE_FILE = re.compile(r"^==FILE== (.+)$")
RE_COUNT = re.compile(r"^count (\S+): (\d+)$")
RE_POINT = re.compile(r"^point id=(-?\d+) x=(\S+) y=(\S+) z=(\S+)$")
RE_LINE = re.compile(r"^line id=(-?\d+) pts=(.*)$")
RE_SURF = re.compile(r"^surf id=(-?\d+) lines=(.*)$")
RE_SOLID = re.compile(r"^solid id=(-?\d+) surfs=(.*)$")


def parse(log_path: Path = LOG):
    out = {}
    cur = None
    for raw in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if line.startswith("==FILE== "):
            cur = {"path": line[9:].strip(), "counts": {}, "points": {}, "lines": {},
                   "surfaces": {}, "solids": {}}
            out[cur["path"]] = cur
            continue
        if cur is None:
            continue
        if line == "==ENDFILE==":
            cur = None
            continue
        m = RE_COUNT.match(line)
        if m:
            cur["counts"][m.group(1)] = int(m.group(2))
            continue
        m = RE_POINT.match(line)
        if m:
            cur["points"][int(m.group(1))] = [float(m.group(2)), float(m.group(3)),
                                              float(m.group(4))]
            continue
        m = RE_LINE.match(line)
        if m:
            pts = [int(x) for x in m.group(2).split()]
            cur["lines"][int(m.group(1))] = pts
            continue
        m = RE_SURF.match(line)
        if m:
            cur["surfaces"][int(m.group(1))] = [int(x) for x in m.group(2).split()]
            continue
        m = RE_SOLID.match(line)
        if m:
            cur["solids"][int(m.group(1))] = [int(x) for x in m.group(2).split()]
            continue
    return out


def stats(data=None):
    data = data if data is not None else parse()
    gt = json.loads(GT.read_text(encoding="utf-8"))
    ok = bad = 0
    print(f"{'file':40s} {'pts':>5} {'lines':>6} {'surfs':>6} {'sols':>5}  gate")
    rows = sorted(data.items(), key=lambda kv: os.path.basename(kv[0].replace("\\", "/")))
    for path, rec in rows:
        name = os.path.basename(path.replace("\\", "/"))
        g = gt.get(path, {}).get("counts", {})
        c = rec["counts"]
        match = all(c.get(k, 0) == (g.get(k, 0) or 0)
                    for k in ("points", "lines", "surfaces", "solids"))
        ok += match
        bad += (not match)
        # 拓扑完整性
        lp_ok = sum(1 for v in rec["lines"].values() if len(v) >= 2)
        sl_ok = sum(1 for v in rec["surfaces"].values() if len(v) >= 1)
        print(f"{name[:39]:40s} {len(rec['points']):>5} {len(rec['lines']):>6} "
              f"{len(rec['surfaces']):>6} {len(rec['solids']):>5}  "
              f"{'OK' if match else 'MISMATCH'}  line2pt={lp_ok}/{len(rec['lines'])} "
              f"surf2line={sl_ok}/{len(rec['surfaces'])}")
    print(f"\ncount gate: {ok} OK / {bad} MISMATCH  (total {len(rows)})")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"
    if cmd == "harvest":
        lim = int(sys.argv[2]) if len(sys.argv) > 2 else None
        harvest(limit=lim)
    elif cmd == "parse":
        d = parse()
        OUT.write_text(json.dumps(d, ensure_ascii=True), encoding="utf-8")
        print("wrote", OUT, "files:", len(d))
    elif cmd == "stats":
        stats()
