import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
# per seg: first record @+12 (2596?) and @+16 high u16 (eid), check @+32 node row vs oracle
ns=D.find_node_section(p)
hi,count,base,stride,idoff,chain=ns
row_map={i:i for i in range(1,count+1)}
row_count=count
import re
oracle={}
for line in open('output/ground_truth/elems/SEAT_MODEL.hm.elems.txt',encoding='utf-8'):
    mm=re.match(r'E (\d+) cfg=(\d+) nodes=(.*)',line.strip())
    if mm: oracle[int(mm.group(1))]=(int(mm.group(2)),tuple(int(x) for x in mm.group(3).split()))
for (sh,segid,c71,cnt,X,Y) in D.find_elem_segments(p):
    if Y!=2: continue
    g=D._parse_a_type(p,sh,cnt,row_count,row_map)
    if not g: continue
    # sample first eid's offset
    for eid in list(g.keys())[:1]:
        dnds=[d[1] for d in g[eid] if d[0]==208 or d[0]==104][:1]
        if dnds and eid in oracle:
            ond=tuple(x for x in oracle[eid][1] if x!=0)
            off=ond[0]-dnds[0][0] if dnds[0] and ond else None
            print('segid=%d cnt=%d eid=%d offset=%s'%(segid,cnt,eid,off))