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
# 错误点（v2 解码错）
ERR = [12726, 12921, 12981, 12994, 12947, 12980, 13216, 11531, 12997, 13114]
# 找块位置
blocks = {}
i = 0
n = len(p)
while i < n - 8:
    v = u32(i)
    if v in pts and u32(i + 4) == 1:
        blocks[v] = i
        i += 8
    else:
        i += 1
for pid in ERR:
    b = blocks.get(pid)
    x, y, z = pts[pid]
    zi = abs(z - round(z)) < 1e-4
    # 真偏移
    toff = None
    for j in range(max(0, b - 0x120), min(b + 0x20, n - 24)):
        xs, ys, zs = d64(j), d64(j + 8), d64(j + 16)
        if abs(xs - x) < 2e-3 and abs(ys - y) < 2e-3 and abs(zs - z) < 2e-3:
            toff = j - b
            break
    out.append(f"  {pid}: z={z} 整数z={zi} 真偏移={toff}")
open("output/ground_truth/ws_err2.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
