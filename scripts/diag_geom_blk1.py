"""dump geometry block1 精确字节布局 (CONST @ sh+404)."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\abaqus\geometry.hm")
sh = 259682
C = sh + 404  # CONST
print(f"sh={sh} CONST={C}")
# dump 640 bytes from CONST as u16
for off in range(0, 620, 2):
    q = C + off
    v = u16(p, q)
    print(f"  C+{off:3d} (abs {q:6d}): {p[q:q+2].hex(' ')} u16={v:<6d}")
