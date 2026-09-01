import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/joints.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
from decoder import u32,u16
ns=D.find_node_section(p)
hi,count,base,stride,idoff,chain=ns
row_map={}; row=0
xoff=24 if stride==96 else 12
for k in range(count):
    rec=base+k*stride
    nid=u32(p,rec+idoff)
    row+=1; row_map[row]=nid
row_count=len(row_map)
sh=127516; cnt=4
gm=D._parse_cfg55_mpc(p,sh,cnt,row_count,row_map)
print('seg11 cfg55_mpc keys:', sorted(gm.keys()) if gm else None)
# check seat-style branch on rec1 eid6073
cp=127676
print('rec1 eid6073 field scan:')
for off in (4,12,14,18,20,22,26,30,32,36):
    if off%2==0 and off+2<=len(p):
        pass
print('  u16@+4=%d u16@+18=%d u16@+22=%d u16@+26=%d u16@+30=%d'%(u16(p,cp+4),u16(p,cp+18),u16(p,cp+22),u16(p,cp+26),u16(p,cp+30)))
print('  u32@+24=%d u32@+28=%d u32@+32=%d'%(u32(p,cp+24),u32(p,cp+28),u32(p,cp+32)))