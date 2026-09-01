import gzip,struct
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
# seg7 @171252 cnt=4, seg8 @170960 cnt=2
# inspect seg7 exact: CONST within [171252+16, 171576-4) (before seg6)
for (sh,cnt,label) in [(171252,4,'seg7'),(170960,2,'seg8')]:
    print("=== %s @%d cnt=%d ==="%(label,sh,cnt))
    # scan for CONST strictly in segment range
    recs=[]; pos=sh+16
    # determine end: next seg6 @171576 for seg7; seg7 @171252 for seg8
    end = 171576 if label=='seg7' else 171252
    while pos<end:
        if is_const(u32(p,pos)): recs.append(pos)
        pos+=4
    print("  CONST count in range:", len(recs), recs)
    for k,cp in enumerate(recs[:8]):
        eid=u16(p,cp+18)
        print("   @%d eid@+18=%d words:"%(cp,eid), " ".join("%08x"%u32(p,cp+w*4) for w in range(10)))
