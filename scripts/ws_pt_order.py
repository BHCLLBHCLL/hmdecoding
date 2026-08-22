import sys, gzip, struct, json
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
def u32(o): return struct.unpack_from("<I", p, o)[0]
out = []
pt_blocks = []
for i in range(0, len(p) - 24):
    if u32(i + 4) == 1 and u32(i + 8) == 0 and u32(i + 12) == 0 and u32(i + 16) == 0:
        pid = u32(i)
        if 10000 <= pid <= 20000:
            pt_blocks.append((i, pid, u32(i - 4)))
out.append(f"point blocks: {len(pt_blocks)}")
pos = json.load(open("output/ground_truth/ws_pt_positions.json"))
pos = {int(k): v for k, v in pos.items()}
pairs = [(b, pid, pos.get(pid)) for b, pid, lead in pt_blocks if pid in pos]
out.append(f"with mapping: {len(pairs)}")
s_by_block = sorted(pairs, key=lambda x: x[0])
s_by_tri = sorted(pairs, key=lambda x: x[2] if x[2] is not None else 0)
blk_rank = {pid: k for k, (b, pid, t) in enumerate(s_by_block)}
tri_rank = {pid: k for k, (b, pid, t) in enumerate(s_by_tri)}
same = sum(1 for pid in blk_rank if blk_rank[pid] == tri_rank.get(pid))
out.append(f"block order == triple order: {same}/{len(pairs)}")
for b, pid, lead in sorted(pt_blocks, key=lambda x: x[0])[:8]:
    t = pos.get(pid)
    out.append(f"  block@0x{b:x} id={pid} lead={lead} triple@0x{(t or 0):x}")
open("output/ground_truth/ws_pt_order.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
