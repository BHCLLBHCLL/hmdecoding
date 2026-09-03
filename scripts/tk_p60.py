import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/truck.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
ns=D.find_node_section(p)
hi,count,base,stride,idoff,chain=ns
row_map={}; row=0
xoff=24 if stride==96 else 12
for k in range(count):
    rec=base+k*stride
    nid=u32(p,rec+idoff)
    row+=1; row_map[row]=nid
row_count=len(row_map)
import sys as s2
s2.path.insert(0,'hmdecoder')
# find which parser gives eid 220195 cfg60
for (sh,segid,c71,cnt,X,Y) in D.find_elem_segments(p):
    if Y!=2: continue
    g=D._parse_a_type(p,sh,cnt,row_count,row_map)
    if g and 220195 in g:
        recs=[d for d in g[220195] if d[0]==60]
        if recs:
            print('segid',segid,'a_type eid220195 cfg60:',recs[0])
            break