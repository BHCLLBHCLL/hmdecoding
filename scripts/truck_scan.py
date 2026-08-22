
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32
p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
print("truck len:", len(p))
hits = []
i = 0
while i < len(p) - 40:
    if u32(p, i + 8) == 1 and u32(p, i + 12) == 136:
        n = u32(p, i + 16)
        if 1 <= n <= 10_000_000:
            hits.append((i, n))
    i += 2
print("hits:", hits[:10])
