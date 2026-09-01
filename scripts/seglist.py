import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
# rebuild row_map like decode() does
# use decoder's own decode to get counts per seg via decode_elements? We'll call parse_nodes
from decoder import is_const,u32,u16,d64
segs=D.find_elem_segments(p)
for (sh,segid,c71,cnt,X,Y) in segs:
    print('seg',segid,'cnt',cnt)