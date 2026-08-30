
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\hm-ansys_contact_manager_2-d_tutorial.hm")
# id 232 @100361; check id 233/234 positions under 68B vs 56B
for stride in (68, 56):
    ids = [u32(p, 100361 + i*stride) for i in range(6)]
    xs = [d64(p, 100361 + i*stride + 12) for i in range(6)]
    print(f"stride {stride}: ids={ids}")
    print(f"   xs={[round(x,2) for x in xs]}")
