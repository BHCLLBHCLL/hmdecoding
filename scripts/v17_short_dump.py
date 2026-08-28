"""v17 SHORT 段字节级 dump: 对比 Y=2 family-1 记录与 SHORT 段记录布局."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64, is_const, find_elem_segments

p = open("output/ground_truth/v17_payload.bin", "rb").read()
segs = sorted(find_elem_segments(p), key=lambda s: s[0])

def seg_hi(sh):
    for s2 in segs:
        if s2[0] > sh:
            return s2[0]
    return len(p)

def dump_record(pos, n=52, label=""):
    print(f"-- rec @{pos} {label}")
    for off in range(0, n, 4):
        b = p[pos+off:pos+off+4]
        v = u32(p, pos+off)
        note = " CONST" if is_const(v) else ""
        print(f"  +{off:3d}: {b.hex(' ')}  u32={v:<10d} u16=({u16(p,pos+off)},{u16(p,pos+off+2)}){note}")

# ---- 1) Y=2 段首记录 (family-1 基准) ----
y2 = [s for s in segs if s[5] == 2]
sh = y2[0][0]
print(f"== Y=2 seg @{sh} segid={y2[0][1]} cnt={y2[0][3]}")
j = p.find(b"\xf5\x1f", sh, seg_hi(sh))
while j >= 0 and not is_const(u32(p, j)):
    j = p.find(b"\xf5\x1f", j + 1, seg_hi(sh))
print(f"first CONST rec @{j}")
dump_record(j, 56, "Y=2 family-1")

# ---- 2) SHORT 段样本 dump ----
samples = {}
for s in segs:
    if s[5] != 2 and s[1] not in samples:
        samples[s[1]] = s
# 选不同 Y 值的段
want = [100026, 2000486, 6500113, 6500114, 200001, 2000949]
for segid in want:
    s = samples.get(segid)
    if not s:
        continue
    sh, _, cfg71, cnt, X, Y = s
    hi = seg_hi(sh)
    print(f"\n== SHORT seg {segid} @{sh} cfg={cfg71} cnt={cnt} X={X} Y={Y} hi={hi} span={hi-sh}")
    # 段头 24 字节
    print("  header:", p[sh:sh+24].hex(' '))
    # 段内所有 CONST 记录位置
    j = sh
    n_const = 0
    while n_const < 2:
        j = p.find(b"\xf5\x1f", j, hi)
        if j < 0:
            break
        if is_const(u32(p, j)):
            dump_record(j, 56, f"seg {segid} const#{n_const}")
            n_const += 1
        j += 1
    if n_const == 0:
        print("  (no CONST record in seg; dump raw from sh+24)")
        dump_record(sh + 24, 56, "raw sh+24")
