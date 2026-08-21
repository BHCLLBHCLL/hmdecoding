import gzip, struct, re

raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])
def f32(off): return struct.unpack_from("<f", p, off)[0]

# x array start: rows 1..3 x = 5,5,5 (f32 0x40A00000)
pat = struct.pack("<fff", 5.0, 5.0, 5.0)
hits = [m.start() for m in re.finditer(re.escape(pat), p)]
print("f32 (5,5,5) hits:", [hex(h) for h in hits[:10]])
# z array: -5.0 f32 run
patz = struct.pack("<f", -5.0)
hitsz = [m.start() for m in re.finditer(re.escape(patz), p)]
print("-5.0 f32 hits:", len(hitsz))
# find LONGEST run of identical -5.0 f32s
best = (0, 0, 0)
i = 0
n = len(p)
while i < n - 4:
    if struct.unpack_from("<f", p, i)[0] == -5.0:
        j = i
        while j < n - 4 and struct.unpack_from("<f", p, j)[0] == -5.0:
            j += 4
        if j - i > best[0]:
            best = (j - i, i, j)
        i = j
    else:
        i += 4
print("longest -5.0 f32 run:", best[0] // 4, "values at 0x%x..0x%x" % (best[1], best[2]))
# y array start: rows 1..3 y = -5,-5,-4.5
paty = struct.pack("<fff", -5.0, -5.0, -4.5)
hitsy = [m.start() for m in re.finditer(re.escape(paty), p)]
print("f32 (-5,-5,-4.5) hits:", [hex(h) for h in hitsy[:10]])
# x values at rows 77, 128, 419, 420, 442: 2.5, 0.5, -3, -3.5, -1 — check near the longest run
for v in (2.5, 0.5, -3.0, -3.5, -1.0):
    patv = struct.pack("<f", v)
    offs = [m.start() for m in re.finditer(re.escape(patv), p)]
    print(f"f32 {v}: {len(offs)} hits {[hex(o) for o in offs[:10]]}")
