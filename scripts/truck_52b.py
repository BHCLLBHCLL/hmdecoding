import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
from decoder import u32,u16,d64
fn='C:/Program Files/Altair/2019/tutorials/hm/truck.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
ns=D.find_node_section(p)
hi,count,base,stride,idoff,chain=ns
k=209424; rec=base+k*stride
print('truck residual k=%d rec=%d 52B dump:'%(k,rec))
for off in range(0,52,4):
    print('  +%02d: %08x'%(off,u32(p,rec+off)))
print('--- normal neighbor k=209425:' )
rec2=base+(k+1)*stride
for off in range(0,52,4):
    print('  +%02d: %08x'%(off,u32(p,rec2+off)))