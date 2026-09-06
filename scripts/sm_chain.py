import sys
sys.path.insert(0, 'hmdecoder')
from decoder import load_payload, u32, d64

p = load_payload(r'C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm')
# find_node_section: (110269, 34296, 110293, 56, 44, True)
base = 110293
stride = 56
def rec(k): return base + k * stride
for k in range(17360, 17390):
    nid_field = u32(p, rec(k) + 44)
    nid = nid_field - 1
    x = d64(p, rec(k)); y = d64(p, rec(k) + 8); z = d64(p, rec(k) + 16)
    print('k=%d @+44=%d -> nid=%d coord=(%g,%g,%g)' % (k, nid_field, nid, x, y, z))
print('--- 34260..34330 ---')
for k in range(34258, 34330):
    nid_field = u32(p, rec(k) + 44)
    nid = nid_field - 1
    x = d64(p, rec(k)); y = d64(p, rec(k) + 8); z = d64(p, rec(k) + 16)
    print('k=%d @+44=%d -> nid=%d coord=(%g,%g,%g)' % (k, nid_field, nid, x, y, z))
