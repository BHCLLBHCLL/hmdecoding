import sys
sys.path.insert(0, 'hmdecoder')
from decoder import load_payload, u16, u32

p = load_payload(r'C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/frame_assembly_1.hm')

# all records with known oracle ids
# (offset, oracle_id, name, next_offset)
comps = [
    (1293108, 1, 'Front_Truss_1', 1293183),
    (1293183, 2, 'Front_Truss_2', 1293258),
    (1293258, 3, 'Con_Frt_Truss', 1293333),
    (1293925, 12, 'Con_Rear_Truss', 1294009),
    (1294009, 14, 'C_^_6_11_HEX', 1294091),
    (1294091, 15, 'C_^_7_11_HEX', 1294173),
    (1294173, 16, 'C_^_8_11_HEX', 1294255),
    (1294255, 17, 'C_^_9_11_HEX', 1294337),
    (1294337, 18, 'C_^_10_11_HEX', 1294419),
]
props = [
    (2351437, 1, 'P_^_6_11_HEX', 2351544),
    (2351544, 2, 'P_^_7_11_HEX', 2351651),
    (2351865, 5, 'P_^_10_11_HEX', None),
]
mats = [
    (2352115, 2, 'M_^_6_11', 2352348),
    (2352348, 3, 'M_^_7_11', 2352581),
    (2353047, 6, 'M_^_10_11', None),
]

print('=== comps: next-id at noff-16? ===')
for off, eid, nm, noff in comps:
    if noff is None:
        continue
    v = u16(p, noff - 16)
    print('%s id=%d  noff-16 u16=%d  (expect next=%d)' % (nm, eid, v, (14 if eid==12 else eid+1)))

print('=== props ===')
for off, eid, nm, noff in props:
    if noff is None:
        continue
    v = u16(p, noff - 16)
    print('%s id=%d  noff-16 u16=%d  (expect next=%d)' % (nm, eid, v, eid+1))

print('=== mats ===')
for off, eid, nm, noff in mats:
    if noff is None:
        continue
    v = u16(p, noff - 16)
    print('%s id=%d  noff-16 u16=%d  (expect next=%d)' % (nm, eid, v, eid+1))
