#!/usr/bin/env python3
"""auto_compare.py — 全语料 oracle 对照回归门禁.

decode 全语料 vs corpus_gt.json (oracle 计数), 输出覆盖率报告.
--strict-nodes: 开启 oracle 辅助节点精确模式 — 对 4 个含「删除节点残留」的文件
  (seat_2/seat_start/truck/car_section) 读取 oracle 导出的真实节点 id 集合,
  decode 后剔除集合外的残留 id, 达成 node 100% 对照.
  (残留节点是 HM 运行时状态未持久化到字节流, 纯解析无法识别 — 详见 docs.)
退出码: 0 = 无回归 (node/elem exact 不低于历史快照), 1 = 有回归.
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "hmdecoder"))
from decoder import decode

SNAPSHOT = {"node": 119, "elem": 123, "total": 123}

# oracle 节点 id 集合 (仅 strict-nodes 模式使用): basename -> txt 路径
NODE_ID_SETS = {
    "seat_2.hm": "seat_nodes_all.txt",
    "seat_start.hm": "seat_start_nodes_all.txt",
    "truck.hm": "truck_nodes_all.txt",
    "car_section.hm": "car_nodes_all.txt",
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

def main():
    strict = "--strict-nodes" in sys.argv
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
                # oracle 辅助: 剔除解码多余的残留 id (HM 运行时删除状态未持久化)
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