import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/solid_map.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
from decoder import u32,u16,d64
# real node candidates: base=4396 (nid12) & 334580 (nid20). Dump surrounding 52B records
def dump_near(base,label):
    print('=== %s base=%d ==='%(label,base))
    # adjacent records: is there a stream of valid nid+coords before/after?
    for k in range(-2,4):
        rec=base+k*52
        if rec<0 or rec+52>len(p): continue
        nid=u32(p,rec+8)
        x,y,z=d64(p,rec+12),d64(p,rec+20),d64(p,rec+28)
        print('  k=%d rec=%d nid=%d x=%g y=%g z=%g'%(k,rec,nid,x,y,z))
dump_near(4396,'nid12')
dump_near(334580,'nid20')