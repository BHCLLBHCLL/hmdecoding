import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/abaqus/abaqus_contactManager_2D_tutorial.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
segs=D.find_elem_segments(p)
sh=[s[0] for s in segs if s[1]==1][0]
s=sh+24; rec=s+8
print('seg1 rec0 @',rec)
for k in range(4):
    slots=0
    while slots<12 and u16(p,rec+2+4*slots)!=0 and u16(p,rec+2+4*slots+2)==0: slots+=1
    ne=u16(p,rec+2+4*slots+4) if slots else 0
    print('k=%d slots=%d next_eid@+%d=%d'%(k,slots,rec+2+4*slots+4,ne))
    rec=rec+34  # stride