
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\wing_section_complete.hm")
# search for u32 1739 anywhere near 85549
for probe in (1739, 1740, 1741):
    hit = [i for i in range(85000, 86000) if u32(p, i) == probe]
    print(f"u32 {probe} near 85549:", hit)
# search E1739 rows [570,598,956,569] and eid as u16 pair around
# dump 85500 exact bytes
print("bytes 85537..85557:", p[85537:85557].hex(" "))
# where is row 570 (first E1739 row)? find u16 570 near 85540-85560
for i in range(85520, 85570):
    if u16(p, i) == 570:
        print(f"u16 570 @{i}")
