import sys,os,re
sys.path.insert(0,'hmdecoder')
from decoder import decode
def load(ef):
    o={}
    for line in open(ef,encoding='utf-8'):
        mm=re.match(r'E (\d+) cfg=(\d+) nodes=(.*)',line.strip())
        if mm:
            eid=int(mm.group(1)); cfg=int(mm.group(2))
            nds=tuple(x for x in (int(x) for x in mm.group(3).split()) if x!=0)
            o[eid]=(cfg,nds)
    return o
# frame_assembly (hm dir) vs lsdyna dir 分别测
m=decode('C:/Program Files/Altair/2019/tutorials/hm/frame_assembly.hm')
dec={}
for e in m.elements:
    dec.setdefault(e.id,[]).append((e.config,tuple(e.nodes)))
o=load('output/ground_truth/elems/frame_assembly.hm.elems.txt')
# find a diff element (same cfg same count but different nodes)
for eid,(cfg,nds) in o.items():
    dc=[d for d in dec.get(eid,[]) if d[0]==cfg]
    if dc and dc[0][1]!=nds and len(dc[0][1])==len(nds):
        print('eid',eid,'cfg',cfg)
        print('  oracle',nds)
        print('  decoded',dc[0][1])
        break