
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\wing_section_complete.hm")
# E1739 record head @85502 (non-aligned MARK), eid@+33, verify formula
for j, exp_eid in ((85502, 1739), (85573, 1740), (85644, 1741)):
    L = u32(p, j + 4)
    eid_off = 28 + L
    eid = u32(p, j + eid_off)
    print(f"j={j} L={L} eid_off={eid_off} eid={eid} (expect {exp_eid})")
    # rows
    if L == 5:
        rows = [u16(p, j + eid_off + 14 + 2*i) for i in range(6)]
    else:
        rows = [u32(p, j + eid_off + 12 + 4*i) >> 16 for i in range(6)]
    print(f"  rows(first 6): {rows}")
