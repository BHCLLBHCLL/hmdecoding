import gzip,struct
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/abaqus/abaqus_contactManager_2D_tutorial.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
import struct as st
db=st.unpack_from('<d',p,4)[0]
print("db_version double",db)
sh=32459; cnt=430
s=sh+24
print("head u32 s,s+4,s+8=",hex(u32(p,s)),hex(u32(p,s+4)),hex(u32(p,s+8)))
rec=s+8
# instrument: walk records
first_eid=1
for k in range(cnt):
    slots=0
    while slots<40 and u16(p,rec+2+4*slots)!=0 and u16(p,rec+2+4*slots+2)==0:
        slots+=1
    nds=[u16(p,rec+2+4*j) for j in range(slots)] if slots else []
    # next_eid at rec+2+4*slots+4
    ne=u16(p,rec+2+4*slots+4) if rec+2+4*slots+4+2<=len(p) else 0
    if k<8 or k>=376:
        print(f"k={k} rec@{rec} slots={slots} nds={nds} next_eid={ne} eid={first_eid+k}")
    if k<8:
        # also dump raw around record
        pass
    if slots<1:
        print(f"  BREAK at k={k}: slots<1 rec@{rec} u32={[hex(u32(p,rec+j)) for j in range(0,24,4)]}")
        break
    # next record: find next slot pattern
    nxt=None
    for j in range(rec+2+4*slots+8, min(rec+50000,len(p)-8)):
        if not (u16(p,j)!=0 and u16(p,j+2)!=0 and u16(p,j+4)==0 and u16(p,j+6)!=0 and u16(p,j+8)==0):
            continue
        t_slots=0
        while t_slots<40 and u16(p,j+2+4*t_slots)!=0 and u16(p,j+2+4*t_slots+2)==0:
            t_slots+=1
        t_nds=[u16(p,j+2+4*t) for t in range(t_slots)] if t_slots else []
        if not t_slots: continue
        t_ne=u16(p,j+2+4*t_slots+4)
        if t_ne==first_eid+k+2:
            nxt=(j,t_slots,t_nds,t_ne); break
    if nxt is None:
        print(f"  NEXT NOT FOUND at k={k} (eid={first_eid+k}) rec@{rec} slots={slots}")
        # dump next 40 bytes for manual inspection
        print("  bytes:", " ".join(f"{u16(p,j):04x}" for j in range(rec,rec+80,2)))
        break
    rec=nxt[0]
