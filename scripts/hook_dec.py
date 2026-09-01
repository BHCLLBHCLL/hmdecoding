import sys,os,gzip
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/samcef/hook.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
# build row_map like decode: parse nodes then row_map = identity-ish. Use decoder decode direct.
from decoder import decode
m=decode(fn)
print('hook total elems:', len(m.elements))
# per seg
segs=D.find_elem_segments(p)
# need row_map/row_count; use decode internals - just call decode_elements with a fake? Instead inspect decode() node count
print('len(m.nodes)', len(m.nodes) if hasattr(m,'nodes') else 'n/a')