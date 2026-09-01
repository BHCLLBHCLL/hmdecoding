import gzip,struct
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
sh=171576
# gather CONST positions
c=[]
pos=sh+16; end=min(sh+2600,len(p))
while pos<end:
    if is_const(u32(p,pos)): c.append(pos)
    pos+=4
# oracle: eid -> (cfg, nodes)
oracle={
1529:(55,[1668,245,577,590,1488]),
1530:(55,[96,342]),
1531:(55,[90,1535]),
1532:(55,[846,1304]),
1533:(55,[173,1305]),
1534:(55,[1388,942]),
1535:(55,[1384,967]),
1536:(55,[139,1538]),
1537:(55,[148,1566]),
1538:(55,[1568,1548]),
1539:(55,[275,542]),
1540:(55,[253,1473]),
1541:(55,[280,578]),
1542:(55,[1355,1085]),
1543:(55,[1358,1113]),
1544:(55,[1147,1357]),
1545:(55,[813,1377]),
1546:(55,[1138,1362]),
1547:(55,[957,941]),
1548:(55,[522,1154]),
1549:(55,[495,112]),
}
# For each CONST rec, find its length (to next CONST)
for k,cp in enumerate(c[:24]):
    endp = c[k+1] if k+1<len(c) else end
    ln = endp-cp
    eid = u16(p,cp+18)
    flag = u32(p,cp+28)
    # rows: find row values at end (from where? try reading u32s)
    print("rec@%d len=%d eid@+18=%d flag=%x"%(cp,ln,eid,flag))
