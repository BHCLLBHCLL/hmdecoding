import gzip,struct
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/abaqus/abaqus_contactManager_2D_tutorial.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
rec=45513
# dump raw from rec, show 4-byte aligned u32 and u16 pairs 200 bytes
print("=== bytes from rec=%d (u16) ==="%rec)
for j in range(rec, rec+120, 2):
    print(f"@{j}: {u16(p,j):04x}", end="  ")
print()
print("=== find all 4-slot-ish records near region 47000..len with node<600 ===")
# scan for slot records: [X][n1][0][n2][0][n3][0][n4][0][next]
cand=[]
for j in range(45513, min(45513+60000,len(p)-8)):
    # check pattern u16(j)!=0? Actually X u16 at j, n1 at j+2, 0 at j+4, n2 at j+6, 0 at j+8
    if u16(p,j+2)!=0 and u16(p,j+4)==0 and u16(p,j+6)!=0 and u16(p,j+8)==0 and u16(p,j+10)!=0 and u16(p,j+12)==0:
        # 4-slot? check j+14, j+16
        slots=0
        while slots<12 and u16(p,j+2+4*slots)!=0 and u16(p,j+2+4*slots+2)==0:
            slots+=1
        ne=u16(p,j+2+4*slots+4) if j+2+4*slots+6<=len(p) else 0
        nds=[u16(p,j+2+4*t) for t in range(slots)]
        if 1<=slots<=6 and all(1<=n<600 for n in nds):
            cand.append((j,slots,nds,ne))
# print candidates in first region and around 45513-48000
print("candidates near break (45500..48000):")
for c in cand:
    if 45500<=c[0]<=48000: print("  ",c)
print("total candidates found in scan range:", len(cand))
print("candidate offsets range:", (cand[0][0], cand[-1][0]) if cand else None)
