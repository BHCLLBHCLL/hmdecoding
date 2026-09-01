import sys
sys.path.insert(0,'hmdecoder')
from decoder import decode
m=decode('C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm')
dec_ids=set(m.nodes.keys())
oracle_ids=set(int(x.strip()) for x in open('output/ground_truth/seat_nodes_all.txt',encoding='utf-8') if x.strip().isdigit())
print('decoded',len(dec_ids),'oracle',len(oracle_ids))
extra=dec_ids-oracle_ids
missing=oracle_ids-dec_ids
print('EXTRA (decoded but not oracle):', sorted(extra))
print('MISSING (oracle but not decoded):', sorted(missing))