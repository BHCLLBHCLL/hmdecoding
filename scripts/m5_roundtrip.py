#!/usr/bin/env python3
"""M5 round-trip 验证: decode -> .hmj JSON -> reload -> 等价性.

按 DEV_PLAN.md §5 M5.2/M5.4 要求, 三同门禁:
  1. count 同: nodes/elems/comps/mats/props/groups 数量
  2. content 同: 节点坐标 (相对容差 1e-9) + 单元 (id/config/nodes/comp)
  3. collector 同: comps/mats/props/groups 名称表

不导入 hm_gui (依赖 PyQt5), 而是用同等 JSON schema 直接 dump/load HMModel,
保证 .hmj 工程文件可独立于 GUI 验证.

用法:
  python scripts/m5_roundtrip.py <input.hm>
  python scripts/m5_roundtrip.py corpus/synthetic/v1913_geom01_p1.hm
退出码 0 = round-trip 等价, 非 0 = 差异 (打印 diff 摘要).
"""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from hmdecoder.decoder import decode, HMModel, Node, Elem, DisplayPoint, GeoPoint


def to_hmj_dict(m):
    """与 hm_gui.EditableModel.to_dict() 同 schema (format_version=1)."""
    return {
        "app": "hm_roundtrip_test", "format_version": 1,
        "db_version": m.db_version,
        "element_variant": m.element_variant,
        "source": "",
        "nodes": [[n.id, n.x, n.y, n.z]
                  for n in sorted(m.nodes.values(), key=lambda v: v.id)],
        "elements": [[e.id, e.config, list(e.nodes), e.comp]
                     for e in m.elements],
        "display_points": [[p.id, p.x, p.y, p.z]
                           for p in m.display_points.values()],
        "geo_points": [[p.id, p.x, p.y, p.z]
                       for p in m.geo_points.values()],
        "comps": m.comps, "mats": m.mats,
        "props": m.props, "groups": m.groups,
        "others": [[i, n] for i, n in m.others],
    }


def from_hmj_dict(d):
    m = HMModel(db_version=d.get("db_version", 0.0),
                element_variant=d.get("element_variant", ""))
    m.nodes = {int(r[0]): Node(int(r[0]), float(r[1]), float(r[2]), float(r[3]))
               for r in d.get("nodes", [])}
    m.elements = [Elem(int(r[0]), [int(v) for v in r[2]], int(r[1]),
                       comp=int(r[3]) if len(r) > 3 else 0)
                  for r in d.get("elements", [])]
    m.display_points = {int(r[0]): DisplayPoint(int(r[0]), float(r[1]), float(r[2]), float(r[3]))
                        for r in d.get("display_points", [])}
    m.geo_points = {int(r[0]): GeoPoint(int(r[0]), float(r[1]), float(r[2]), float(r[3]))
                    for r in d.get("geo_points", [])}
    m.comps = {int(k): v for k, v in d.get("comps", {}).items()}
    m.mats = {int(k): v for k, v in d.get("mats", {}).items()}
    m.props = {int(k): v for k, v in d.get("props", {}).items()}
    m.groups = {int(k): v for k, v in d.get("groups", {}).items()}
    m.others = [(int(r[0]), r[1]) for r in d.get("others", [])]
    return m


def main(path):
    p = Path(path)
    if not p.exists():
        print(f"NOT FOUND: {p}")
        return 2
    print(f"[1/4] decode: {p}")
    src = decode(str(p))
    print(f"      db={src.db_version} nodes={len(src.nodes)} "
          f"elems={len(src.elements)} "
          f"comps={len(src.comps)} mats={len(src.mats)} "
          f"props={len(src.props)} groups={len(src.groups)} "
          f"geo={len(src.geo_points)}")

    print(f"[2/4] dump -> .hmj")
    with tempfile.NamedTemporaryFile("w", suffix=".hmj", delete=False) as f:
        tmp = Path(f.name)
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(to_hmj_dict(src), f)

    print(f"[3/4] reload from .hmj")
    with open(tmp, "r", encoding="utf-8") as f:
        reloaded = from_hmj_dict(json.load(f))

    print(f"[4/4] diff")
    diffs = []

    def cmp(name, a, b):
        if a != b:
            diffs.append(f"{name}: {a!r} != {b!r}")

    cmp("nodes count", len(src.nodes), len(reloaded.nodes))
    cmp("elems count", len(src.elements), len(reloaded.elements))
    cmp("comps count", len(src.comps), len(reloaded.comps))
    cmp("mats count", len(src.mats), len(reloaded.mats))
    cmp("props count", len(src.props), len(reloaded.props))
    cmp("groups count", len(src.groups), len(reloaded.groups))
    cmp("geo_points count", len(src.geo_points), len(reloaded.geo_points))
    cmp("display_points count", len(src.display_points), len(reloaded.display_points))
    cmp("db_version", src.db_version, reloaded.db_version)

    # 节点坐标逐项 (相对容差)
    miss = 0
    for nid, n in src.nodes.items():
        rn = reloaded.nodes.get(nid)
        if rn is None:
            miss += 1
            continue
        for ax, (a, b) in enumerate(((n.x, rn.x), (n.y, rn.y), (n.z, rn.z))):
            if abs(b) < 1e-12:
                rel = abs(a - b)
            else:
                rel = abs(a - b) / max(abs(a), abs(b), 1e-30)
            if rel > 1e-9:
                miss += 1
                if miss <= 5:
                    diffs.append(f"node {nid} axis {ax}: {a!r} vs {b!r}")
    if miss:
        diffs.append(f"node coord mismatches: {miss}")

    # 元素逐项
    em_cnt = len(src.elements)
    rm_cnt = len(reloaded.elements)
    if em_cnt != rm_cnt:
        diffs.append(f"elem list length: {em_cnt} vs {rm_cnt}")
    else:
        for i, (se, re) in enumerate(zip(src.elements, reloaded.elements)):
            if se.id != re.id or se.config != re.config \
                    or list(se.nodes) != list(re.nodes) or se.comp != re.comp:
                if len(diffs) < 20:
                    diffs.append(f"elem[{i}]: src={se!r} got={re!r}")

    # collector 名称表
    for label, src_d, rel_d in (("comps", src.comps, reloaded.comps),
                                  ("mats", src.mats, reloaded.mats),
                                  ("props", src.props, reloaded.props),
                                  ("groups", src.groups, reloaded.groups)):
        sks = sorted(src_d.items())
        rks = sorted(rel_d.items())
        if sks != rks:
            diffs.append(f"{label}: src has {len(sks)}, reload has {len(rks)}")
            for k, v in list((set(sks) ^ set(rks)))[:5]:
                diffs.append(f"  {label}[{k}] diff: {v!r}")

    # others 列表序
    if list(src.others) != list(reloaded.others):
        diffs.append(f"others list differs ({len(src.others)} vs "
                f"{len(reloaded.others)})")

    tmp.unlink()
    if diffs:
        print("DIFFS:")
        for d in diffs[:30]:
            print(" ", d)
        if len(diffs) > 30:
            print(f"  ... and {len(diffs) - 30} more")
        print(f"RESULT: FAIL ({len(diffs)} diffs)")
        return 1
    print(f"RESULT: OK (counts+content+collectors all equal)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))