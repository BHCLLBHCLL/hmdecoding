import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/joints.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
sh=80020; cnt=1
# find CONST records in seg3 region
recs=[]; pos=sh+16; end=min(sh+400,len(p))
while pos<end:
    if is_const(u32(p,pos)): recs.append(pos)
    pos+=4
print('seg3 CONSTs:', recs[:3])
cp=80108
print('rec0 dump:')
for off in range(0,72,4):
    print('  @+%03d: %08x'%(off,u32(p,cp+off)))