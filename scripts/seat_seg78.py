import gzip,struct
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
for (sh,cnt,label) in [(170960,2,'seg8'),(171252,4,'seg7')]:
    print("=== %s @%d cnt=%d ==="%(label,sh,cnt))
    recs=[]; pos=sh+16; end=min(sh+400,len(p))
    while pos<end:
        if is_const(u32(p,pos)): recs.append(pos)
        pos+=4
    for k,cp in enumerate(recs[:cnt]):
        eid=u16(p,cp+18); nsl=u32(p,cp+32); master=u32(p,cp+36)
        slaves=[u32(p,cp+48+4*j) for j in range(nsl)]
        print("  rec%d eid=%d nsl=%d nds=[%d]+%s"%(k,eid,nsl,master,slaves))
