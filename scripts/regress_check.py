"""回归抽查: 关键文件 @+8hi 修复后元素计数是否退化."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import decode

cases = [
    (r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\SEAT_MODEL.hm", 27503, "SEAT_MODEL"),
    (r"C:\Program Files\Altair\2019\tutorials\hm\frame_assembly_1.hm", None, "frame_assembly_1"),
    (r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\frame_assembly_3.hm", 11953, "frame_assembly_3"),
    (r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm", 212489, "truck"),
]
for path, exp_elem, name in cases:
    m = decode(path)
    print(f"{name}: nodes={len(m.nodes)} elems={len(m.elements)} (expected elems={exp_elem})")
