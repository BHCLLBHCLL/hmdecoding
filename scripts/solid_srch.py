import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/solid_map.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
import struct as st
print('db_version double:', st.unpack_from('<d',p,4)[0])
# search for node ids 12 and 20 as [id][0][k] patterns (68B)
from decoder import u32
for target in (12,20):
    print('search nid', target,':')
    cnt=0
    for i in range(len(p)-12):
        if u32(p,i)==target and u32(p,i+4)==0:
            print('   @%d pat nid=%d [0] then u32@+8=%d'%(i,target,u32(p,i+8)))
            cnt+=1
            if cnt>8: break