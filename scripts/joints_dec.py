import sys,os,gzip
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/joints.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
# row_count from node parse: use decode() value
from decoder import decode
m=decode(fn)
print('joints elems:', len(m.elements))
# per seg: try parse and count. We need row_map. Build from node section via decode internals is hard; instead just probe config at each.
segs=D.find_elem_segments(p)
for (sh,segid,c71,cnt,X,Y) in segs:
    print(' segid=%d cnt=%d X=%d Y=%d'%(segid,cnt,X,Y))