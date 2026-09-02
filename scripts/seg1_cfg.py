import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/joints.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
ns=D.find_node_section(p)
hi,count,base,stride,idoff,chain=ns
row_map={}; row=0
xoff=24 if stride==96 else 12
for k in range(count):
    rec=base+k*stride
    nid=struct.unpack_from('<I',p,rec+idoff)[0]
    row+=1; row_map[row]=nid
row_count=len(row_map)
# seg1 Y=2 a_type output: what eids/configs
sh=[s[0] for s in D.find_elem_segments(p) if s[1]==1][0]
cnt=[s[3] for s in D.find_elem_segments(p) if s[1]==1][0]
got=D._parse_a_type(p,sh,cnt,row_count,row_map)
eids=sorted(got.keys())
print('seg1 a_type eids:', eids[:8],'...',eids[-3:], 'n=',len(eids))
for eid in eids[:4]:
    print('  eid',eid,'->',[(c,tuple(n)[:6]) for c,n in got[eid]])