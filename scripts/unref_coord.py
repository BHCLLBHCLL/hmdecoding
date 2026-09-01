import sys,os
sys.path.insert(0,'hmdecoder')
from decoder import decode
for label,fn,expected in [('truck','C:/Program Files/Altair/2019/tutorials/hm/truck.hm',[2220530]),('car_section','C:/Program Files/Altair/2019/tutorials/hm/car_section.hm',[26806,26807])]:
    m=decode(fn)
    ref=set()
    for e in m.elements: ref.update(e.nodes)
    node_ids=set(m.nodes.keys())
    unreferenced=[nid for nid in node_ids if nid not in ref]
    print('%s unreferenced:'%label)
    for nid in sorted(unreferenced):
        n=m.nodes[nid]
        zero = (n.x==0 and n.y==0 and n.z==0)
        print('   nid=%d x=%g y=%g z=%g zero=%s'%(nid,n.x,n.y,n.z,zero))