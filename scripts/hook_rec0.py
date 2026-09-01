import gzip,struct
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/samcef/hook.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
cp=731874+16  # rec0 approx; use exact from earlier: rec0 at 731874+?
# rec0 was printed; find exact const offset
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
recs=[]; pos=731874+16; end=min(731874+400,len(p))
while pos<end:
    if is_const(u32(p,pos)): recs.append(pos)
    pos+=4
cp=recs[0]
print('rec0 @',cp)
for off in range(0,68,4):
    v=u32(p,cp+off)
    print('  +%02d: %08x  u16[%d]=%d u16[%d]=%d'%(off,v,off,v&0xffff,off+2,v>>16))