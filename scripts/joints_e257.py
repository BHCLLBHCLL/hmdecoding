import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/joints.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
# search eid 257 (0x101) markers
print('eid 257 (0x101) occurrences:')
for i in range(len(p)-8):
    if u16(p,i)==0x101 and u16(p,i+2)==0:
        # plausible eid u16 marker
        print('  @%d u16=257'%i)
        if i>50000: break