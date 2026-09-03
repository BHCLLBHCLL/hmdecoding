import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
# oracle valid node ids (sorted)
valid=sorted(int(x.strip()) for x in open('output/ground_truth/sm_nodes_all.txt',encoding='utf-8') if x.strip().isdigit())
print('valid node count',len(valid))
# build filtered row_map: row -> valid[row-1]
row_map={i:valid[i-1] for i in range(1,len(valid)+1)}
# eid 20995 had row 17506 -> node?
print('filtered row_map[17506] =', row_map.get(17506), '(oracle node should be that elem node)')
print('decode before: row 17506 -> 17506 (wrong), oracle node 17523')