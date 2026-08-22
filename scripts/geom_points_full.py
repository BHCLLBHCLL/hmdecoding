import sys, gzip, struct
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm")
def u32(o): return struct.unpack_from("<I", p, o)[0]
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
# 全 payload 扫描: 找所有 (x,y,0) 且 id 合理的 52B 显示记录（宽松）
recs = []
i = 0
while i < len(p) - 52:
    x, y, z = d64(i), d64(i + 8), d64(i + 16)
    rid = u32(i + 40)
    if abs(x) < 1000 and abs(y) < 1000 and z == 0.0 and 0 < rid < 100000:
        recs.append((i, rid, round(x, 2), round(y, 2)))
        i += 52
    else:
        i += 4
out.append(f"z=0 显示记录总数: {len(recs)}")
for r in recs:
    out.append(f"  @0x{r[0]:x} id={r[1]} ({r[2]}, {r[3]}, 0)")
open("output/ground_truth/geom_points_full.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
