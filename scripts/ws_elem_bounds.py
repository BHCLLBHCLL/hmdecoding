import sys, gzip, struct, re
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
ns = D.find_node_section(p)
hdr, count, shift, idoff, coordoff = ns[0]
nodes, base = D.parse_nodes(p, hdr, count, shift, idoff, coordoff)
row_order = [D.u32(p, base + k * 52 + idoff) for k in range(count)]
row_of = {nid: k + 1 for k, nid in enumerate(row_order)}
def u16(o): return struct.unpack_from("<H", p, o)[0]
def u32(o): return struct.unpack_from("<I", p, o)[0]

# find section start: walk backward from 302871@0xe46cd
eid0 = 302871
pos = 0xe46cd
start = pos
while start - 30 >= 0:
    prev_eid = u32(start - 30)
    if prev_eid == u32(start) + 1:
        start -= 30
    else:
        break
print("section start:", hex(start), "first eid:", u32(start))
# walk forward to find section end
end = start
while True:
    next_eid = u32(end + 30)
    if next_eid == u32(end) - 1 and end + 30 < len(p):
        end += 30
    else:
        break
print("section end:", hex(end), "last eid:", u32(end))
print("count:", (end - start) // 30 + 1)
# check what's before start and after end
print("before start:", p[start-16:start].hex())
print("after end:", p[end+30:end+46].hex())
