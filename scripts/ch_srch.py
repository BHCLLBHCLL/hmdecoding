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
inv={v:k for k,v in row_map.items()}
print('node2614->row', inv.get(2614), '695->', inv.get(695))
print('node2613->row', inv.get(2613), '696->', inv.get(696), '697->', inv.get(697))
sh=326009
want=[inv.get(2614),inv.get(695),inv.get(2613),inv.get(696),inv.get(697)]
print('want rows:', want)
for off in range(24,200,2):
    v=u16(p,sh+off)
    if v in want:
        print('  row %d at +%d'%(v,off))