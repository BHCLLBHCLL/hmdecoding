import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/solid_map.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
from decoder import u32,d64
# v11 52B-flat: nid = u32@+8, coords @+12/+20/+28. Find base where base+8==12 or 20 with valid stride
import math
def is_float(v):
    try: return abs(v)<1e6
    except: return False
print('search 52B-flat base giving nid 12 or 20:')
cap=len(p)-52
for base in range(0,cap,4):
    nid=u32(p,base+8)
    if nid in (12,20):
        x=d64(p,base+12); y=d64(p,base+20); z=d64(p,base+28)
        if abs(x)<1e6 and abs(y)<1e6 and abs(z)<1e6:
            print('  base=%d nid=%d x=%g y=%g z=%g'%(base,nid,x,y,z))