import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/joints.hm'
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
row_count=len(row_map)
sh=80020; cnt=1
gm=D._parse_cfg55_mpc(p,sh,cnt,row_count,row_map)
print('seg3 cfg55_mpc:', sorted(gm.keys()) if gm else None)
# eid 497 nodes check: c22 = u16@+22 & 0xFF
cp=80108
print('u16@+22=%d &0xFF=%d  (want 22)'%(u16(p,cp+22),u16(p,cp+22)&0xff))
print('u16@+24=%d -> node %s'%(u16(p,cp+24), row_map.get(u16(p,cp+24))))
print('u16@+28=%d -> node %s'%(u16(p,cp+28), row_map.get(u16(p,cp+28))))