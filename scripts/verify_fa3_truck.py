"""验证 fa3 + truck 修复后 eid 集合匹配."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import decode

for path, gt_file, name in [
    (r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\frame_assembly_3.hm",
     "output/ground_truth/fa3_elemids.txt", "frame_assembly_3"),
    (r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm",
     "output/ground_truth/truck_elemids.txt", "truck"),
]:
    m = decode(path)
    lines = open(gt_file).read().splitlines()
    gt = set(int(l) for l in lines if l.strip().isdigit())
    dec = set(m.elements.keys())
    missing = sorted(gt - dec)
    extra = sorted(dec - gt)
    print(f"{name}: decoded={len(dec)} oracle={len(gt)} missing={len(missing)} extra={len(extra)}")
    if missing:
        print(f"   missing 首20: {missing[:20]}")
    if extra:
        print(f"   extra 首20: {extra[:20]}")
