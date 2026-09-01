import sys,os,gzip
sys.path.insert(0,'hmdecoder')
import decoder as D
from decoder import u32,d64
fn='C:/Program Files/Altair/2019/tutorials/hm/car_section.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
ns=D.find_node_section(p)
hi,count,base,stride,idoff,chain=ns
for k in range(count):
    rec=base+k*stride
    nid=u32(p,rec+idoff)
    if nid in (26806,26807):
        x,y,z=d64(p,rec+12),d64(p,rec+20),d64(p,rec+28)
        print('k=%d rec=%d nid=%d x=%g y=%g z=%g'%(k,rec,nid,x,y,z))
        # neighbors
        for kk in (k-1,k+1):
            r2=base+kk*stride
            if 0<=r2 and r2+stride<=len(p):
                n2=u32(p,r2+idoff)
                x2,y2,z2=d64(p,r2+12),d64(p,r2+20),d64(p,r2+28)
                print('   nbr k=%d nid=%d x=%g y=%g z=%g'%(kk,n2,x2,y2,z2))