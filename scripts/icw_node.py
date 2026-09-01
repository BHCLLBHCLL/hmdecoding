import sys,os,gzip
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/icw_ex1.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
from decoder import decode
m=decode(fn)
print('icw_ex1 nodes:', len(m.nodes))
print('node_count attr:', getattr(m,'node_count',None))
print('node_section:', getattr(m,'node_section',None))
ns=D.find_node_section(p)
print('find_node_section:', ns)