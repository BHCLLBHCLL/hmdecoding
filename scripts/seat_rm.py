import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
# build row_map via the decoder's node parse
nodes=D.parse_nodes(p) if hasattr(D,'parse_nodes') else None
# find row_map attribute
import inspect
print([n for n in dir(D) if 'node' in n.lower()])
print([n for n in dir(D) if 'row' in n.lower()])
