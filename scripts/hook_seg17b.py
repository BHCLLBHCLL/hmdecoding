import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/samcef/hook.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
# rebuild row_map per decode() logic: parse_nodes then index
ns,pcfg = D.find_node_section(p)
ens,eidcfg = D.find_node_section_struct(p) if hasattr(D,'find_node_section_struct') else (None,None)
print('node flags:', pcfg)
# Try decoder.decode_elements using its own row_map — but we can't easily. Instead just print what seg17 gets via _parse_a_type
segs=D.find_elem_segments(p)
sh=[s[0] for s in segs if s[1]==17][0]
cnt=[s[3] for s in segs if s[1]==17][0]
# row_count from nodes length approx
row_count=14069
row_map={i:i for i in range(1,row_count+1)}
got=D._parse_a_type(p,sh,cnt,row_count,row_map)
print('seg17 _parse_a_type ->', len(got) if got else 0)