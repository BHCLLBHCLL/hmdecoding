
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\hm-ansys_contact_manager_2-d_tutorial.hm")
hits = []
start = 0
while True:
    i = p.find(b"\x88\x00\x00\x00", start)
    if i < 0: break
    n = u32(p, i + 4)
    hits.append((i, n))
    start = i + 1
print("136 hits:", [(i, n) for i, n in hits if 1 <= n <= 10_000_000][:10])
# also check first node id: manager nodes id?
# dump node area near 90177 (the 92B section) to see id range
for k in range(0, 4):
    rec = 90177 + k * 92
    print(f"rec{k}: id={u32(p, rec+8)} x={__import__('struct').unpack_from('<d', p, rec+12)[0]:.4g}")
