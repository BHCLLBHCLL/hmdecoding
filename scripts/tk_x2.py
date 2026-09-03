import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/truck.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
# find X=2 segments
start=0; x2=[]
while True:
    i=p.find(b'\xe5\x03\x00\x00',start)
    if i<0: break
    if i+24<=len(p):
        segid=u32(p,i+4); c71=u32(p,i+8); cnt=u32(p,i+12); X=u32(p,i+16); Y=u32(p,i+20)
        if X==2 and 100<=c71<=500:
            x2.append((i,segid,cnt,Y))
    start=i+1
print('X=2 segments:',x2)