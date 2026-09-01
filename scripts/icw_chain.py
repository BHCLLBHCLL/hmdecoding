import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/icw_ex1.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
from decoder import u32,d64
base=20088; stride=56; count=89
prev_nid=0
print('chain nodes trace:')
for k in range(count):
    rec=base+k*stride
    if rec+stride>len(p):
        print('  k=%d END-OF-P'%k)
        break
    nid=u32(p,rec+44)-1
    x=d64(p,rec)
    ok= (1<=nid<=10000000 and abs(x)<1e9)
    if not ok:
        print('  BREAK at k=%d nid=%d x=%g'%(k,nid,x))
        for kk in range(max(0,k-3),min(count,k+4)):
            r2=base+kk*stride
            print('     k=%d nid=%d raw=%d'%(kk,u32(p,r2+44)-1,u32(p,r2+44)))
        break
    prev_nid=nid
print('parsed until k, prev_nid=',prev_nid)