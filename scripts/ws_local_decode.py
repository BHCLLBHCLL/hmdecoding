import sys, gzip, struct, json
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
pos = json.load(open("output/ground_truth/ws_pt_positions.json"))
pos = {int(k): v for k, v in pos.items()}

def decode_local():
    """变体 B 点解码器: 扫 [id][1] 块 → 块前 0x100 内最近合理三元组。"""
    results = {}
    i = 0
    n = len(p)
    while i < n - 8:
        v = u32(i)
        if 10000 <= v <= 20000 and u32(i + 4) == 1:
            # 块前 0x100 内找最近合理三元组
            best = None
            for j in range(i - 0x100, i):
                if j < 0 or j + 24 > n:
                    continue
                x, y, z = d64(j), d64(j + 8), d64(j + 16)
                if abs(x) < 1e5 and abs(y) < 1e5 and abs(z) < 1e5 and (abs(x) > 1e-6 or abs(y) > 1e-6 or abs(z) > 1e-6):
                    best = j
                    break  # 最近（从块向前扫第一个）
            if best is not None:
                results[v] = best
            i += 8
        else:
            i += 1
    return results

res = decode_local()
out.append(f"本地关联解码: {len(res)} 个点")
# 验证
ok = 0
bad = []
for pid, t in res.items():
    x, y, z = pts[pid]
    xs, ys, zs = d64(t), d64(t + 8), d64(t + 16)
    err = max(abs(xs - x), abs(ys - y), abs(zs - z))
    if err < 2e-3:
        ok += 1
    else:
        bad.append((pid, (round(xs,3), round(ys,3), round(zs,3)), (x, y, z)))
out.append(f"验证: {ok}/{len(res)} 正确, {len(bad)} 错")
open("output/ground_truth/ws_local_decode.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
