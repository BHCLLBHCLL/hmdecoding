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
for (sh,segid,c71,cnt,X,Y) in D.find_elem_segments(p):
    if X!=3: continue
    g=D._parse_cfg55_mpc(p,sh,cnt,row_count,row_map)
    if g and 219946 in g:
        print('segid',segid,'Y',Y,'cfg55_mpc eid219946:',g[219946])