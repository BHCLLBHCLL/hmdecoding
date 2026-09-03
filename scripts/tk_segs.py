import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/truck.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
import struct as st
print('db:',st.unpack_from('<d',p,4)[0])
segs=D.find_elem_segments(p)
for (sh,segid,c71,cnt,X,Y) in segs[:8]:
    print('  segid=%d cnt=%d X=%d Y=%d'%(segid,cnt,X,Y))
print('... total',len(segs))