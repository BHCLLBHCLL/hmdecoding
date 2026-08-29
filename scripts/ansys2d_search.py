
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\hm-ansys_contact_wizard_2-d_tutorial.hm")
# node section?
from decoder import find_node_section
ns = find_node_section(p)
print("node section:", ns)
# search E1 nodes [1,3,29,28] as u32 seq
seq = [1, 3, 29, 28]
hits = [i for i in range(0, len(p)-16) if all(u32(p, i+j*4) == seq[j] for j in range(4))]
print("E1 u32 hits:", hits[:5])
# also as u16 slots [1,0,3,0,29,0,28,0]
seq2 = [1, 0, 3, 0, 29, 0, 28, 0]
hits2 = [i for i in range(0, len(p)-16) if all(u16(p, i+j*2) == seq2[j] for j in range(8))]
print("E1 u16-slot hits:", hits2[:5])
# eid 1 search
eidhits = [i for i in range(0, len(p)-4) if u32(p, i) == 1]
print("u32==1 near段:", [i for i in eidhits if 21300 < i < 22000][:8])
