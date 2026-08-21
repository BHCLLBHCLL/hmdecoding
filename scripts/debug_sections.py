import sys, gzip, struct
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm")
es = D.find_elem_section(p)
print("elem section candidates:", [(hex(h), n) for h, n in es])
ns = D.find_node_section(p)
print("node section candidates:", [(hex(h), n) for h, n in ns][:6])
# check the record at 0x68c8
i = 0x68c8
print("rec@0x68c8:", [D.u32(p, i + j) for j in range(0, 52, 4)])
