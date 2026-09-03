import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
ns=D.find_node_section(p)
hi,count,base,stride,idoff,chain=ns
row_map={i:i for i in range(1,count+1)}
row_count=count
for (sh,segid,c71,cnt,X,Y) in D.find_elem_segments(p):
    g=D._parse_a_type(p,sh,cnt,row_count,row_map)
    if g and 20995 in g:
        print('segid',segid,'has 20995:',g[20995])