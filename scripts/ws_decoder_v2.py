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

OFFSETS = (-249, -145, -93, -41, 15)
def score_triple(x, y, z):
    """分数: z 整数 + x/y 合理。"""
    s = 0
    if abs(z - round(z)) < 1e-4:
        s += 10
    if abs(x - round(x)) < 1e-4:
        s += 2
    if abs(y - round(y)) < 1e-4:
        s += 2
    return s

def decode_points():
    results = {}
    i = 0
    n = len(p)
    while i < n - 8:
        v = u32(i)
        if 10000 <= v <= 20000 and u32(i + 4) == 1 and v not in results:
            best = None
            for off in OFFSETS:
                j = i + off
                if 0 <= j and j + 24 <= n:
                    x, y, z = d64(j), d64(j + 8), d64(j + 16)
                    if abs(x) < 1e5 and abs(y) < 1e5 and abs(z) < 1e5 and abs(x) > 1 and abs(y) > 1:
                        s = score_triple(x, y, z)
                        if best is None or s > best[0]:
                            best = (s, j, x, y, z)
            if best:
                results[v] = (best[1], best[2], best[3], best[4])
            i += 8
        else:
            i += 1
    return results

res = decode_points()
out.append(f"解码点数: {len(res)}")
ok = 0
bad = []
for pid, (t, x, y, z) in res.items():
    if pid in pts:
        xo, yo, zo = pts[pid]
        err = max(abs(x - xo), abs(y - yo), abs(z - zo))
        if err < 2e-3:
            ok += 1
        else:
            bad.append(pid)
out.append(f"oracle 验证: {ok}/{len(res)} 正确 ({100*ok//len(res)}%), 错 {len(bad)}")
out.append(f"错误点: {bad[:10]}")
open("output/ground_truth/ws_decoder_v2.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
