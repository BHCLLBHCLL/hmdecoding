"""v17 搜索缺失节点 3481964/3481965 的原始字节 + 验证 seg#0 真实末记录."""
import sys, struct
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64

p = open("output/ground_truth/v17_payload.bin", "rb").read()

# oracle 节点集
f = open("output/ground_truth/v17gt_dummy_nodeids.txt")
f.readline(); f.readline()
gt = set(int(l) for l in f if l.strip())
f.close()
print(f"oracle nodes: {len(gt)}")

# 当前解析节点
from decoder import find_node_section_struct, parse_nodes
nodes = {}
for ens in find_node_section_struct(p, multi=True):
    n2, _ = parse_nodes(p, ens)
    nodes.update(n2)
print(f"parsed nodes: {len(nodes)}")
missing = gt - set(nodes)
extra = set(nodes) - gt
print(f"missing: {sorted(missing)}")
print(f"extra: {sorted(extra)}")

# 原始字节搜索
for nid in sorted(missing):
    pat = struct.pack("<I", nid)
    hits = []
    j = 0
    while True:
        j = p.find(pat, j)
        if j < 0:
            break
        hits.append(j)
        j += 1
    print(f"\nnid {nid}: {len(hits)} raw hits")
    for h in hits[:6]:
        lo = max(0, h - 16)
        print(f"  @{h}: ctx={p[lo:h+48].hex(' ')}")
        # 尝试 68B 布局解释
        if h + 68 <= len(p):
            print(f"    68B view: nid={u32(p,h)} z4={u32(p,h+4)} k={u32(p,h+8)} "
                  f"x={d64(p,h+12):.3f} y={d64(p,h+20):.3f} z={d64(p,h+28):.3f}")

# seg#0 真实末记录验证: k=116732 (8135587) 与 k=116733 (8135655)
print("\n== seg#0 tail records ==")
base0, stride0 = 197811, 68
for k in (116730, 116731, 116732, 116733):
    rec = base0 + k * stride0
    print(f"k={k} @{rec}: nid={u32(p,rec)} z4={u32(p,rec+4)} k8={u32(p,rec+8)} "
          f"x={d64(p,rec+12):.3f} tail40..68={p[rec+40:rec+68].hex(' ')}")

# seg#0 中间记录的 tail 模式 (对比)
print("\n== seg#0 mid record tail ==")
for k in (1000, 50000, 100000):
    rec = base0 + k * stride0
    print(f"k={k}: nid={u32(p,rec)} k8={u32(p,rec+8)} tail40..68={p[rec+40:rec+68].hex(' ')}")
