import sys, gzip, struct
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm")
def u32(o): return struct.unpack_from("<I", p, o)[0]
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
# 1d 节点区: header @0xE90? 用解码器定位
ns = D.find_node_section(p)
hdr, count, shift, idoff, coordoff = ns[0]
nodes, base = D.parse_nodes(p, hdr, count, shift, idoff, coordoff)
out.append(f"node base 0x{base:x} count={count}")
# 节点 24 的记录 +0x28
rec24 = None
for k in range(count):
    rec = base + k * 52
    nid = u32(rec + idoff)
    if nid == 24:
        rec24 = rec
        break
if rec24:
    nxt = u32(rec24 + 0x28)
    out.append(f"节点 24 @0x{rec24:x}: +0x28(next)={nxt}")
# 显示点 997 的坐标（应有 (5,-5,-5)）
# 通过标记块提取
marks = [i for i in range(len(p) - 8) if u32(i) == 0x40008126]
found = {}
for m in marks:
    off = u32(m + 4)
    for start in range(off, min(off + 0x40, len(p) - 52)):
        x, y, z = d64(start), d64(start + 8), d64(start + 16)
        rid = u32(start + 40)
        if abs(x) < 1e6 and abs(y) < 1e6 and abs(z) < 1e6 and 0 < rid < 2000:
            found[rid] = (round(x, 2), round(y, 2), round(z, 2))
out.append(f"显示点 997: {found.get(997)}")
out.append(f"显示点 24: {found.get(24)}")
out.append(f"显示点 75: {found.get(75)}")
out.append(f"显示点 443: {found.get(443)}")
# 节点 next 值统计
nexts = {}
for k in range(count):
    rec = base + k * 52
    nid = u32(rec + idoff)
    nxt = u32(rec + 0x28)
    nexts[nid] = nxt
out.append(f"节点24 next={nexts.get(24)} 节点25 next={nexts.get(25)} 节点26 next={nexts.get(26)}")
out.append(f"节点443 next={nexts.get(443)} 节点465 next={nexts.get(465)}")
open("output/ground_truth/next_display.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
