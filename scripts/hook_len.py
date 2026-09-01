import gzip,struct
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/samcef/hook.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
cp=731898
# next CONST after cp
nxt=None
for j in range(cp+4, min(cp+400,len(p)-4)):
    if is_const(u32(p,j)): nxt=j; break
print('next CONST @',nxt,'len=',nxt-cp)
# dump full record
for off in range(0,(nxt-cp)+20,4):
    v=u32(p,cp+off)
    print('  +%02d: %08x'%(off,v))