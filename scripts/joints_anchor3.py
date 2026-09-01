import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/joints.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
ns=D.find_node_section(p)
hi,count,base,stride,idoff,chain=ns
row_map={}; row=0
xoff=24 if stride==96 else 12
for k in range(count):
    rec=base+k*stride
    nid=u32(p,rec+idoff)
    row+=1; row_map[row]=nid
cp=127552
print('eid=',u32(p,cp+4),'nslave@+46=',u16(p,cp+46),'master@+50=',u16(p,cp+50))
print('master->node:', row_map.get(u16(p,cp+50)))
print('u32@+52..:', [u32(p,cp+52+4*t) for t in range(6)])
print('cand slaves u16@+56..:', [u16(p,cp+52+4*t) for t in range(10)])
print('oracle eid6072 nodes:', [6899, 7695,7697,7699,7701,7703,7705,7707,7709,7711])