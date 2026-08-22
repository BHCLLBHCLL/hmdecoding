
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64
p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\SEAT_MODEL.hm")
print("bytes 110293..110309:", p[110293:110309].hex(" "))
print("u32(110293):", u32(p, 110293))
print("u32(110297):", u32(p, 110297))
print("d64(110293):", d64(p, 110293))
print("d64(110297):", d64(p, 110297))
print("d64(110301):", d64(p, 110301))
