import sys
sys.path.insert(0, 'hmdecoder')
from decoder import decode
m = decode(r'C:/Program Files/Altair/2019/tutorials/hm/icw_ex1.hm')
oracle = {}
cur = None
for line in open('output/ground_truth/nc_all.log', encoding='utf-8'):
    line = line.strip()
    if line.startswith('==FILE=='):
        cur = line.split('==FILE== ', 1)[1]
    elif line.startswith('N '):
        p = line.split()
        if cur and 'icw_ex1.hm' in cur:
            oracle[int(p[1])] = (float(p[2]), float(p[3]), float(p[4]))
print('oracle icw_ex1 nodes', len(oracle), 'decode', len(m.nodes))
for nid in range(80, 90):
    o = oracle.get(nid)
    nd = m.nodes.get(nid)
    if o or nd:
        print('nid', nid, 'ora =', o, 'dec =', (nd.x, nd.y, nd.z) if nd else None)
