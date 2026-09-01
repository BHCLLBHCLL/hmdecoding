import gzip,struct
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
# oracle eid -> nodes (from seat_mpc.txt, full tail)
oracle={
1529:[1668,245,577,590,1488],1530:[96,342],1531:[90,1535],1532:[846,1304],1533:[173,1305],
1534:[1388,942],1535:[1384,967],1536:[139,1538],1537:[148,1566],1538:[1568,1548],
1539:[275,542],1540:[253,1473],1541:[280,578],1542:[1355,1085],1543:[1358,1113],
1544:[1147,1357],1545:[813,1377],1546:[1138,1362],1547:[957,941],1548:[522,1154],
1549:[495,112],1550:[1632,184,188,1580,1581,1631],1551:[1629,1185,1187,1189,1190,1630],
1552:[1633,766,1179,1181,1182,1634],1553:[1636,843,1416,1592,1593,1635],1554:[1649,27,31,1612,1611,1652],
1555:[1653,482,483,480,481,1656],1556:[1657,488,492,493,491,1658],1557:[1660,104,109,1613,1614,1659],
1558:[1666,776,1097,1116,1387],1559:[1665,1226,1231,1235,1237],1560:[1667,425,426,427,431],
1561:[1667,1668],1562:[1666,1665],
}
# gather CONST records across tail region 170960..174800
recs=[]
pos=170960; end=min(174800,len(p))
while pos<end:
    if is_const(u32(p,pos)): recs.append(pos)
    pos+=4
print("total CONST in tail region:", len(recs))
# decode each using layout
ok=0
for cp in recs:
    eid=u16(p,cp+18)
    n=u32(p,cp+32)+1
    master=u32(p,cp+36)
    slaves=[u32(p,cp+48+4*k) for k in range(max(0,n-1))]
    nds=[master]+slaves
    exp=oracle.get(eid)
    m = "OK" if exp and exp==nds else "MISMATCH"
    if exp and exp==nds: ok+=1
    print("eid=%d n=%d nds=%s exp=%s %s"%(eid,n,nds,exp,m))
print("matched", ok, "of", len(recs))
