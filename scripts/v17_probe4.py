"""v17 row_map 验证 + SHORT 段记录多假设检验."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, is_const, find_node_section_struct

p = open("output/ground_truth/v17_payload.bin", "rb").read()

ns_list = [ens for ens in find_node_section_struct(p, multi=True) if ens[1] >= 50]
row_of = {}
nid_of = {}
row = 0
for cfg in sorted(ns_list, key=lambda s: s[2]):
    hi, count, base2, stride, idoff, chain = cfg
    for k in range(count):
        nid = u32(p, base2 + k * stride + idoff)
        row += 1
        row_of[nid] = row
        nid_of[row] = nid

# 1) 验证 eid=1 rows [94,818,817,820] -> oracle nodes
print("eid=1 rows->nids:", [nid_of.get(r) for r in (94, 818, 817, 820)],
      "expect [2006765, 2129498, 2129497, 2129500]")

f = open("output/ground_truth/v17gt_dummy_elemids.txt")
f.readline(); f.readline()
gt = set(int(l) for l in f if l.strip())
f.close()

# 2) gt 成员检查
for v in (589209, 131704, 64921, 365000, 365001, 365002, 3912279, 3912280, 3912281, 3912282):
    print(f"eid {v} in oracle: {v in gt}")

# 3) rows 183520/183523/50939/50940 -> nids
print("rows->nids:", {r: nid_of.get(r) for r in (183520, 183523, 50939, 50940)})

# 4) dump 多个 SHORT 段首记录
def dump_rec(sh, label, n=96):
    j = p.find(b"\xf5\x1f", sh + 16, sh + 400)
    while j >= 0 and not is_const(u32(p, j)):
        j = p.find(b"\xf5\x1f", j + 1, sh + 400)
    if j < 0:
        print(f"\n== {label}: no const record found near {sh}")
        return
    # 记录长度: 到下一个 const
    k2 = p.find(b"\xf5\x1f", j + 4, j + 2000)
    while k2 >= 0 and not is_const(u32(p, k2)):
        k2 = p.find(b"\xf5\x1f", k2 + 1, j + 2000)
    rlen = (k2 - j) if k2 >= 0 else -1
    print(f"\n== {label} @ {j} len={rlen}")
    for off in range(0, min(n, rlen if rlen > 0 else n), 4):
        v = u32(p, j + off)
        note = " CONST" if is_const(v) else ""
        print(f"  {off:+4d}: {p[j+off:j+off+4].hex()} u32={v:>10d} u16=({u16(p,j+off)},{u16(p,j+off+2)}){note}")

dump_rec(40564251, "seg 100026 Y=9 cnt=1")
dump_rec(48676171, "seg 500050 Y=9 cnt=88")
dump_rec(38019435, "seg 6500114 Y=10 cnt=51")
dump_rec(44261519, "seg 200052 Y=5 cnt=1")
