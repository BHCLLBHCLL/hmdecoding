import sys, gzip, struct
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
def u32(o): return struct.unpack_from("<I", p, o)[0]
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
pts = {}
for line in open("output/ground_truth/ws_allpoints.log", encoding="utf-8").read().splitlines():
    parts = line.split()
    if len(parts) == 5:
        pts[int(parts[1])] = (float(parts[2]), float(parts[3]), float(parts[4]))

def decode_block_points():
    """变体 B 点解码器: 扫 [id][1] 块 → 块内滑动找首个合理三元组。"""
    results = {}
    i = 0
    n = len(p)
    while i < n - 8:
        v = u32(i)
        if 10000 <= v <= 20000 and u32(i + 4) == 1:
            # 块内 (i-0x20..i+0x100) 滑动找三元组（坐标合理）
            best = None
            for j in range(max(0, i - 0x20), min(i + 0x100, n - 24)):
                x, y, z = d64(j), d64(j + 8), d64(j + 16)
                if abs(x) < 1e5 and abs(y) < 1e5 and abs(z) < 1e5 and (abs(x) > 1e-6 or abs(y) > 1e-6 or abs(z) > 1e-6):
                    best = j
                    break
            if best is not None:
                results[v] = best
            i += 8
        else:
            i += 1
    return results

res = decode_block_points()
out.append(f"块内解码: {len(res)} 个点")
ok = 0
bad = []
for pid, t in res.items():
    x, y, z = pts[pid]
    xs, ys, zs = d64(t), d64(t + 8), d64(t + 16)
    err = max(abs(xs - x), abs(ys - y), abs(zs - z))
    if err < 2e-3:
        ok += 1
    else:
        bad.append((pid, hex(t), (round(xs,4), round(ys,4), round(zs,4)), (round(x,4), round(y,4), round(z,4))))
out.append(f"验证: {ok}/{len(res)} 正确, {len(bad)} 错")
for b in bad[:8]:
    out.append(f"  bad: {b}")
open("output/ground_truth/ws_block_decode.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
