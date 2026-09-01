import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/channel_brkt_assem_analysis.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
ns=D.find_node_section(p)
print('node section:', ns)
hi,count,base,stride,idoff,chain=ns
row_map={}; row=0
xoff=24 if stride==96 else 12
for k in range(count):
    rec=base+k*stride
    nid=u32(p,rec+idoff)
    row+=1; row_map[row]=nid
print('row_count', len(row_map))
# eid 2432->nodes [2614,695]; find row refs
# Looking at seg4: @+40=0x982=2434 eid. Need the 3 records.
# guess records are at sh+? Let me find 2432/2433/2434 markers
sh=326009
for off in range(24,240,4):
    v=u32(p,sh+off)
    if v in (0x980,0x981,0x982):
        print('eid marker %08x at +%d'%(v,off))