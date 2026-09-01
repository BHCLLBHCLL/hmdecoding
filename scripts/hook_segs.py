import gzip,struct
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/hook.hm'
import os
print('exists', os.path.exists(fn))
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
segs=[]
start=0
while True:
    i=p.find(b"\xe5\x03\x00\x00",start)
    if i<0: break
    if i+24<=len(p):
        segid=u32(p,i+4); c71=u32(p,i+8); cnt=u32(p,i+12); X=u32(p,i+16); Y=u32(p,i+20)
        if X in (2,3) and 100<=c71<=500 and 1<=cnt<=10000000 and Y<10000000:
            segs.append((i,segid,c71,cnt,X,Y))
    start=i+1
for s in segs: print(' off=%d segid=%d cnt=%d X=%d Y=%d'%s)