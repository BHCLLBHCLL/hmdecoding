import sys,os
sys.path.insert(0,'hmdecoder')
from decoder import decode
# sanity: seat_2 strict filter
m=decode('C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm')
ids=set(int(x.strip()) for x in open('output/ground_truth/seat_nodes_all.txt',encoding='utf-8') if x.strip().isdigit())
kept=[nid for nid in m.nodes if nid in ids]
removed=[nid for nid in m.nodes if nid not in ids]
print('seat_2: total',len(m.nodes),'kept',len(kept),'removed',removed)
assert len(kept)==1620 and removed==[149], 'unexpected'
print('SANITY OK')