#!/usr/bin/env python3
"""auto_compare.py — 全语料 oracle 对照回归门禁.

decode 全语料 vs corpus_gt.json (oracle 计数), 输出覆盖率报告.
开关:
  --strict-nodes: oracle 辅助节点精确模式 (4 文件删除残留剔除) — node 100%.
  --content:      内容级逐元素对照 (对已有 oracle 元素列表的文件): eid/config/节点精确比对.
退出码: 0 = 无回归, 1 = 有回归.
"""
import sys, os, json, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "hmdecoder"))
from decoder import decode

SNAPSHOT = {"node": 119, "elem": 123, "total": 123}

NODE_ID_SETS = {
    "seat_2.hm": "seat_nodes_all.txt",
    "seat_start.hm": "seat_start_nodes_all.txt",
    "truck.hm": "truck_nodes_all.txt",
    "car_section.hm": "car_nodes_all.txt",
}

# 内容级对照的 oracle 元素列表: basename -> txt 路径
ELEM_ID_SETS = {
    "joints.hm": "joints_all.txt",
    "seat_2.hm": "seat2_elems_all.txt",
    "abaqus_contactManager_2D_tutorial.hm": "abq2d_elems_all.txt",
    "hook.hm": "hook_elems_all.txt",
}

def load_node_ids(gt_dir, name):
    p = os.path.join(gt_dir, name)
    if not os.path.exists(p):
        return None
    ids = set()
    for line in open(p, encoding="utf-8"):
        t = line.strip()
        if t.isdigit():
            ids.add(int(t))
    return ids or None

def content_compare(m, gt_dir, name):
    """逐元素内容对照: 返回 (same_cfg, diff_cfg, same_nds, diff_nds, only_dec, only_ora)."""
    p = os.path.join(gt_dir, name)
    if not os.path.exists(p):
        return None
    dec = {}
    for e in m.elements:
        dec.setdefault(e.id, []).append((e.config, tuple(e.nodes)))
    oracle = {}
    for line in open(p, encoding="utf-8"):
        mm = re.match(r'E (\d+) cfg=(\d+) nodes=(.*)', line.strip())
        if mm:
            eid = int(mm.group(1)); cfg = int(mm.group(2))
            nds = tuple(x for x in (int(x) for x in mm.group(3).split()) if x != 0)
            oracle[eid] = (cfg, nds)
    same_cfg = diff_cfg = same_nds = diff_nds = only_dec = only_ora = 0
    for eid, (cfg, nds) in oracle.items():
        if eid not in dec:
            only_ora += 1; continue
        dc = [d for d in dec[eid] if d[0] == cfg]
        if dc:
            same_cfg += 1
            if any(d[1] == nds for d in dc):
                same_nds += 1
            else:
                diff_nds += 1
        else:
            diff_cfg += 1
    for eid in dec:
        if eid not in oracle:
            only_dec += 1
    return (same_cfg, diff_cfg, same_nds, diff_nds, only_dec, only_ora)

def main():
    strict = "--strict-nodes" in sys.argv
    content = "--content" in sys.argv
    gt_dir = os.path.join(os.path.dirname(__file__), "..", "output", "ground_truth")
    gt = json.load(open(os.path.join(gt_dir, "corpus_gt.json")))
    n_ok = e_ok = total = 0
    strict_files = 0
    misses = []
    for path, info in gt.items():
        if not os.path.exists(path):
            continue
        total += 1
        try:
            m = decode(path)
        except Exception as ex:
            misses.append((os.path.basename(path), "CRASH", 0, 0))
            continue
        exp_n = info["counts"]["nodes"]; exp_e = info["counts"]["elements"]
        node_len = len(m.nodes)
        if strict and exp_n:
            set_name = NODE_ID_SETS.get(os.path.basename(path), "")
            idset = load_node_ids(gt_dir, set_name) if set_name else None
            if idset is not None and len(idset) == exp_n:
                node_len = len([nid for nid in m.nodes if nid in idset])
                strict_files += 1
        if exp_n == 0 or node_len == exp_n:
            n_ok += 1
        else:
            misses.append((os.path.basename(path), "node", node_len, exp_n))
        if exp_e == 0 or len(m.elements) == exp_e:
            e_ok += 1
        else:
            misses.append((os.path.basename(path), "elem", len(m.elements), exp_e))
        if content:
            set_name = ELEM_ID_SETS.get(os.path.basename(path), "")
            if set_name:
                r = content_compare(m, gt_dir, set_name)
                if r:
                    print(f"CONTENT {os.path.basename(path)}: same_cfg={r[0]} diff_cfg={r[1]} same_nds={r[2]} diff_nds={r[3]} only_dec={r[4]} only_ora={r[5]}")
    print(f"total={total} node-ok={n_ok} elem-ok={e_ok} strict={strict} strict_files={strict_files}")
    print(f"node-exact {n_ok}/{total} (snapshot {SNAPSHOT['node']})")
    print(f"elem-exact {e_ok}/{total} (snapshot {SNAPSHOT['elem']})")
    for mn in misses:
        print("  X", mn)
    ok = n_ok >= SNAPSHOT["node"] and e_ok >= SNAPSHOT["elem"]
    print("PASS" if ok else "REGRESSION")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())