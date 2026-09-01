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
cp=127552
master=u16(p,cp+50); slaves=[u16(p,cp+62+4*t) for t in range(9)]
print('master row',master,'->node',row_map.get(master))
print('slave rows',slaves)
print('slave nodes',[row_map.get(s) for s in slaves])
print('expect master 6899, slaves 7695,7697,7699,7701,7703,7705,7707,7709,7711')