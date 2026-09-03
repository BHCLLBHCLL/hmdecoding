import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/truck.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
# eid 219946 = 0x35B3A. find in a cfg55_mpc segment (Y=1 or Y=2)
# search element record
for (sh,segid,c71,cnt,X,Y) in D.find_elem_segments(p):
    cp=None
    for off in range(sh+16,sh+200,4):
        if is_const(u32(p,off)): cp=off; break
    if cp and u32(p,cp+4)==219946:
        print('segid',segid,'cfg55 record @',cp)
        for off in range(0,80,4):
            print('  +%02d: %08x'%(off,u32(p,cp+off)))
        break