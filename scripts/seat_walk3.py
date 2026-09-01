import gzip,struct
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
# rec@171668 (eid 1530, 2-node) len 56
for (cp,ln,eid) in [(171668,56,1530),(171600,68,1529),(172788,72,1550)]:
    print("=== rec eid=%d len=%d ==="%(eid,ln))
    for off in range(0,ln,4):
        v=u32(p,cp+off)
        # show u16 halves too
        lo=v&0xFFFF; hi=v>>16
        print("  +%02d: u32=%08x  (u16@+%d=%d, u16@+%d=%d)"%(off,v,off,lo,off+2,hi))
