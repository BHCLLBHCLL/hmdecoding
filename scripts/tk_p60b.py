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
# scan ALL Y=2 segs, all parsers, find eid 220195
for (sh,segid,c71,cnt,X,Y) in D.find_elem_segments(p):
    if X!=3 or Y!=2: continue
    for pname,pf in (('a_type',D._parse_a_type),('y2_c60',D._parse_y2_c60),('cfg55',D._parse_cfg55_mpc),('ansys2d',D._parse_ansys2d_elems)):
        try:
            g=pf(p,sh,cnt,row_count,row_map)
        except Exception:
            continue
        if g and 220195 in g:
            print('segid',segid,pname,'->',g[220195])