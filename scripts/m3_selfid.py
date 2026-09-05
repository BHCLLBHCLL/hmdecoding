import sys
sys.path.insert(0, 'hmdecoder')
from decoder import load_payload, u16, u32

p = load_payload(r'C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/frame_assembly_1.hm')

# (offset, oracle_id, name)
allrecs = [
    (1293108, 1, 'comp Front_Truss_1'),
    (1293183, 2, 'comp Front_Truss_2'),
    (1293925, 12, 'comp Con_Rear_Truss'),
    (1294009, 14, 'comp C_^_6_11_HEX'),
    (1294337, 18, 'comp C_^_10_11_HEX'),
    (2351437, 1, 'prop P_^_6_11_HEX'),
    (2351865, 5, 'prop P_^_10_11_HEX'),
    (2352115, 2, 'mat M_^_6_11'),
    (2353047, 6, 'mat M_^_10_11'),
    (1319044, 1, 'group C_Spotweld_1'),
]
print('id@off-16 hypothesis:')
for off, eid, nm in allrecs:
    v = u16(p, off - 16)
    ok = 'OK' if v == eid else 'MISMATCH'
    print('%s  off=%d  u16(off-16)=%d  oracle=%d  %s' % (nm, off, v, eid, ok))
