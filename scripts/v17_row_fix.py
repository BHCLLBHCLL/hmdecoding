"""v17 row_map 修复诊断: 重复行 116734/116735 的字节级检查 + 缺失节点 3481964/5 小段定位."""
import sys, struct
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64, find_node_section_struct

p = open("output/ground_truth/v17_payload.bin", "rb").read()

# 全部节点段 (不过滤 count>=50, 看小段)
all_segs = find_node_section_struct(p, multi=True)
print(f"all node segs (incl small): {len(all_segs)}")

# 按 base 排序, 给出每段 base/cnt/stride/首尾 nid
segs_sorted = sorted(all_segs, key=lambda s: s[2])
row = 0
dup_info = []
for si, (hi, cnt, base, stride, idoff, chain) in enumerate(segs_sorted):
    first = u32(p, base + idoff)
    last = u32(p, base + (cnt - 1) * stride + idoff)
    r0 = row + 1
    row += cnt
    tag = ""
    if cnt < 50:
        tag = " <-- SMALL (filtered)"
    print(f"seg#{si} base={base} cnt={cnt} stride={stride} rows {r0}..{row} nid {first}..{last}{tag}")
    if r0 <= 116735 <= row:
        dup_info.append((si, base, cnt, stride, r0))

# 重复行字节检查
print("\n== duplicate rows detail ==")
for si, base, cnt, stride, r0 in dup_info:
    for k in range(116730 - r0, min(116742 - r0, cnt)):
        rec = base + k * stride
        rown = r0 + k
        nid = u32(p, rec + 0)
        x, y, z = d64(p, rec + 12), d64(p, rec + 20), d64(p, rec + 28)
        print(f"row {rown}: rec@{rec} nid={nid} k={u32(p, rec + 8)} xyz=({x:.3f},{y:.3f},{z:.3f}) "
              f"tail48={u32(p, rec + 48)} tail52={u32(p, rec + 52)} tail64={u32(p, rec + 64) if stride == 92 else '-'}")

# 缺失节点 3481964/3481965 的存储位置
print("\n== missing nodes 3481964/3481965 location ==")
for nid in (3481964, 3481965):
    pat = struct.pack("<I", nid)
    j = 0
    while True:
        j = p.find(pat, j)
        if j < 0:
            break
        # 检查 68B 布局: [nid][0][k<=16][x][y][z]...
        if j + 68 <= len(p) and u32(p, j + 4) == 0 and 1 <= u32(p, j + 8) <= 16:
            x = d64(p, j + 12)
            if abs(x) < 1e9:
                # 该记录属于哪个段?
                seg = None
                for (hi, cnt, base, stride, idoff, chain) in segs_sorted:
                    if base <= j < base + cnt * stride and (j - base) % stride == 0:
                        seg = (base, cnt, stride, (j - base) // stride)
                        break
                print(f"nid {nid} @ {j}: k={u32(p, j + 8)} xyz=({x:.4f},{d64(p, j + 20):.4f},{d64(p, j + 28):.4f}) seg={seg}")
        j += 1

# 小段 (cnt<50) 的完整列表及其在文件中的位置关系
print("\n== small segs (<50) context ==")
big_bases = [s[2] for s in segs_sorted if s[1] >= 50]
for (hi, cnt, base, stride, idoff, chain) in segs_sorted:
    if cnt >= 50:
        continue
    before = [b for b in big_bases if b < base]
    after = [b for b in big_bases if b > base]
    pb = max(before) if before else None
    na = min(after) if after else None
    first = u32(p, base + idoff)
    print(f"small seg base={base} cnt={cnt} stride={stride} nid0={first} "
          f"prev_big={pb} next_big={na}")
