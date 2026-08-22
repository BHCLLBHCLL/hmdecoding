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
m = D.decode("WS_3.2_3d_tetra_finish.hm")
node_ids = set(m.nodes.keys())
OFFSETS = (-249, -145, -93, -41, 15)
BAD_Y = {2.063}  # 参数类 y 值
def family_vote(j, x, y, z):
    for d in (52, -52, 104, -104):
        j2 = j + d
        if 0 <= j2 and j2 + 24 <= len(p):
            x2, y2, z2 = d64(j2), d64(j2 + 8), d64(j2 + 16)
            if abs(x2 - x) < 1e-4 and abs(y2 - y) < 1e-4 and abs(z2 - z) < 1e-4:
                return True
    return False
results = {}
i = 0
n = len(p)
while i < n - 8:
    v = u32(i)
    if 1 <= v <= 10_000_000 and u32(i + 4) == 1 and v not in results and v not in node_ids:
        best = None
        for off in OFFSETS:
            j = i + off
            if 0 <= j and j + 24 <= n:
                x, y, z = d64(j), d64(j + 8), d64(j + 16)
                if abs(x) < 1e5 and abs(y) < 1e5 and abs(z) < 1e5 and abs(x) > 1 and abs(y) > 1:
                    if any(abs(y - by) < 1e-3 for by in BAD_Y):
                        continue
                    s = 0
                    if abs(z - round(z)) < 1e-4:
                        s += 10
                    if family_vote(j, x, y, z):
                        s += 20
                    if best is None or s > best[0]:
                        best = (s, j, x, y, z)
        if best and best[0] >= 20:
            results[v] = (best[1], best[2], best[3], best[4])
        i += 8
    else:
        i += 1
ok = 0
fp = []
for pid, (t, x, y, z) in results.items():
    if pid in pts:
        xo, yo, zo = pts[pid]
        if max(abs(x - xo), abs(y - yo), abs(z - zo)) < 2e-3:
            ok += 1
        else:
            fp.append(pid)
    else:
        fp.append(pid)
out.append(f"v4: {len(results)} 候选, 真点 {ok}/157, 误报 {len(fp)}")
out.append(f"误报: {fp[:10]}")
open("output/ground_truth/ws_geopt_v4.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
