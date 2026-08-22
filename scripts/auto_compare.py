#!/usr/bin/env python3
"""Phase 4 自动比对器: 对语料文件逐个 decode, 与 ground truth (corpus_gt.json) 计数比对.

用法:
  py scripts/auto_compare.py                 # 全量 (可按 payload 上限过滤)
  py scripts/auto_compare.py --max-payload 1_000_000   # 仅小文件
  py scripts/auto_compare.py --limit 10       # 仅前 N 个文件 (按 payload 升序)

输出:
  output/ground_truth/compare_report.txt      逐文件明细 + 汇总
"""
import sys, time, json, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hmdecoder"))
from decoder import decode

GT = Path(__file__).resolve().parent.parent / "output/ground_truth/corpus_gt.json"
IDX = Path(__file__).resolve().parent.parent / "corpus/corpus_index.json"
OUT = Path(__file__).resolve().parent.parent / "output/ground_truth/compare_report.txt"


def load_index():
    """corpus_index.json: 每文件 {relpath, abs, payload, db_version, layout}."""
    return json.load(open(IDX, encoding="utf-8"))


def load_gt():
    """corpus_gt.json: {abs_path: {counts: {...}, ...}}."""
    return json.load(open(GT, encoding="utf-8"))


def norm(p):
    return p.replace("\\", "/").lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-payload", type=int, default=None, help="仅处理 payload <= 该值的文件")
    ap.add_argument("--limit", type=int, default=None, help="最多处理 N 个文件 (按 payload 升序)")
    ap.add_argument("--timeout", type=float, default=120, help="单文件解码超时 (秒)")
    args = ap.parse_args()

    gt = load_gt()
    idx = load_index()
    # gt 键做路径归一化 (Windows 反斜杠 vs 正斜杠)
    gt_norm = {norm(k): v for k, v in gt.items()}
    # 索引里 payload 已知, 过滤 + 排序
    entries = []
    for e in idx:
        g = gt_norm.get(norm(e["abs"]))
        if g is None:
            rk = norm(e["relpath"])
            hit = next((k for k in gt_norm if k.endswith(rk)), None)
            if hit:
                g = gt_norm[hit]
        if g is not None:
            entries.append((e, g))
    entries.sort(key=lambda x: x[0]["payload"])

    if args.max_payload:
        entries = [x for x in entries if x[0]["payload"] <= args.max_payload]
    if args.limit:
        entries = entries[: args.limit]

    print(f"files to compare: {len(entries)}")
    lines = []
    rows = []
    n_ok_node = n_ok_elem = n_err = 0
    n_node_target = n_elem_target = 0
    for i, (e, g) in enumerate(entries):
        path = e["abs"]
        name = e["relpath"].split("/")[-1]
        counts = g.get("counts", {})
        tn = counts.get("nodes", 0)
        te = counts.get("elements", 0)
        n_node_target += tn
        n_elem_target += te
        t0 = time.time()
        try:
            m = decode(path)
            dn, de = len(m.nodes), len(m.elements)
            dnode = tn - dn
            delem = te - de
            if tn == 0:
                node_st = "skip(0)"
            elif dnode == 0:
                node_st = "OK"
            else:
                node_st = f"miss{dnode:+d}"
            if te == 0:
                elem_st = "skip(0)"
            elif delem == 0:
                elem_st = "OK"
            else:
                elem_st = f"miss{delem:+d}"
            if dnode == 0:
                n_ok_node += 1
            if delem == 0:
                n_ok_elem += 1
            dt = time.time() - t0
            line = f"{name:36s} v{e['db_version']:<6} {e['layout']:<10} payload={e['payload']:>10,} | nodes {dn:>9,}/{tn:>9,} {node_st} | elems {de:>9,}/{te:>9,} {elem_st} | {dt:6.1f}s"
        except Exception as ex:
            n_err += 1
            dt = time.time() - t0
            line = f"{name:36s} v{e['db_version']:<6} {e['layout']:<10} payload={e['payload']:>10,} | ERROR: {type(ex).__name__}: {str(ex)[:60]} | {dt:6.1f}s"
        print(line)
        lines.append(line)
        rows.append((name, tn, te))

    # 汇总
    total_t = sum(float(l.split()[-1].rstrip("s")) for l in lines if l.split()[-1].rstrip("s").replace(".", "").isdigit())
    summary = [
        "",
        "=" * 100,
        f"files: {len(entries)}  errors: {n_err}",
        f"node exact: {n_ok_node}/{len(entries)}  (target {n_node_target:,}, decode {n_node_target - n_ok_node and '' or ''})",
        f"elem exact: {n_ok_elem}/{len(entries)}  (target {n_elem_target:,})",
        f"total decode time: {total_t:.0f}s",
    ]
    for s in summary:
        print(s)
        lines.append(s)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nreport -> {OUT}")


if __name__ == "__main__":
    main()
