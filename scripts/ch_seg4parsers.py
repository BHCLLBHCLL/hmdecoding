import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/channel_brkt_assem_analysis.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
ns=D.find_node_section(p)
hi,count,base,stride,idoff,chain=ns
row_map={}; row=0
xoff=24 if stride==96 else 12
for k in range(count):
    rec=base+k*stride
    nid=u32(p,rec+idoff)
    row+=1; row_map[row]=nid
# y4_elems on seg4 sh=326009
gm=D._parse_y4_elems(p,326009,3,len(row_map),row_map)
print('seg4 _parse_y4_elems:', sorted(gm.keys()) if gm else None)
# cfg55_mpc on seg4
gm2=D._parse_cfg55_mpc(p,326009,3,len(row_map),row_map)
print('seg4 cfg55_mpc:', sorted(gm2.keys()) if gm2 else None)
# a_type
gm3=D._parse_a_type(p,326009,3,len(row_map),row_map)
print('seg4 a_type:', sorted(gm3.keys()) if gm3 else None)