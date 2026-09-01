import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
# replicate decode row_map: find node section
fn='C:/Program Files/Altair/2019/tutorials/hm/keyhole.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
ns=D.find_node_section(p)
print('node section:', ns)
# build row_map like decode()
from decoder import d64,u32,u16
if isinstance(ns,tuple) and len(ns)==6:
    hi,count,base2,stride,idoff,chain = ns
    row_map={}
    row=0
    xoff=24 if stride==96 else 12
    for k in range(count):
        rec=base2+k*stride
        nid=u32(p,rec+idoff)
        row+=1
        row_map[row]=nid
    print('row_map rows 1..6:', [row_map.get(i) for i in range(1,7)])
    print('row_map rows 4..5:', [row_map.get(i) for i in range(4,7)])