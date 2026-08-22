
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\abaqus\crash_tubes.hm")
# E2 nodes [771, 766, 762, 761] as u16 slots [771][0][766][0][762][0][761][0]
seq = [771, 0, 766, 0, 762, 0, 761, 0]
hits = []
for i in range(0, len(p) - 16):
    if all(u16(p, i + j*2) == seq[j] for j in range(8)):
        hits.append(i)
print("E2 slot hits:", hits[:5])
# E1 slots [769, 0, 767, 0, 766, 0, 771, 0]
seq1 = [769, 0, 767, 0, 766, 0, 771, 0]
hits1 = []
for i in range(0, len(p) - 16):
    if all(u16(p, i + j*2) == seq1[j] for j in range(8)):
        hits1.append(i)
print("E1 slot hits:", hits1[:5])
if hits1 and hits:
    print("spacing:", hits[0] - hits1[0])
    # dump E1 record
    rec = hits1[0]
    for off in range(-12, 48, 2):
        print(f"  {off:+3d}: {u16(p, rec+off)}")
