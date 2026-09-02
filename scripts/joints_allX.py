import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/joints.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
start=0; found=[]
while True:
    i=p.find(b'\xe5\x03\x00\x00',start)
    if i<0: break
    if i+24<=len(p):
        segid=u32(p,i+4); c71=u32(p,i+8); cnt=u32(p,i+12); X=u32(p,i+16); Y=u32(p,i+20)
        if 100<=c71<=500 and 1<=cnt<=10000000 and Y<10000000:
            found.append((i,segid,c71,cnt,X,Y))
    start=i+1
for f in found:
    print(' sh=%d segid=%d cnt=%d X=%d Y=%d'%(f[0],f[1],f[3],f[4],f[5]))