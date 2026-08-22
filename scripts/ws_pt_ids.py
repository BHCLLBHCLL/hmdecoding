import sys, gzip, struct, re
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
def u32(o): return struct.unpack_from("<I", p, o)[0]
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
for pid in (11573, 12719, 12784, 12550, 12610):
    hits = [m.start() for m in re.finditer(re.escape(struct.pack("<I", pid)), p)]
    out.append(f"u32 {pid}: {len(hits)} hits {[hex(h) for h in hits[:6]]}")
    for h in hits[:2]:
        # 检查 52B 显示记录模式: id 在 +40
        for off in (h - 40, h):
            if off >= 0:
                x, y, z = d64(off), d64(off + 8), d64(off + 16)
                rid = u32(off + 40)
                if abs(x) < 1e4 and abs(y) < 1e4 and abs(z) < 1e4 and rid == pid:
                    out.append(f"  !! 52B 显示记录 @0x{off:x}: ({round(x,3)}, {round(y,3)}, {round(z,3)}) id={rid}")
open("output/ground_truth/ws_pt_ids.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
