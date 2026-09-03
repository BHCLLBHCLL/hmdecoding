import sys
sys.path.insert(0,'hmdecoder')
from decoder import decode
m=decode('C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm')
# oracle valid node ids (sorted)
oracle=sorted(int(x.strip()) for x in open('output/ground_truth/sm_nodes_all.txt',encoding='utf-8') if x.strip().isdigit())
# decode's chain nodes are 1..34328 (continuous). row_map identity: row->row.
# correct row_map: row k -> k-th valid oracle node id
print('valid node ids:',len(oracle))
# element row 17506 -> which valid node id?
# if decode uses row=node_id (identity), then row 17506 -> node 17506 (which is valid?)
print('17506 in oracle valid:', 17506 in oracle)
print('17523 in oracle valid:', 17523 in oracle)
# correct mapping: row index (0-based) into valid list
print('valid[17506-1] (0-based row 17506):', oracle[17506-1])
print('valid[17523-1]:', oracle[17523-1])
# which row maps to node 17523?
idx=oracle.index(17523)+1
print('node 17523 is at valid row',idx)