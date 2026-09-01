import sys,os
sys.path.insert(0,'hmdecoder')
from decoder import decode
files=[('seat_2','C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm',[149]),('seat_start','C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_start.hm',[149]),('truck','C:/Program Files/Altair/2019/tutorials/hm/truck.hm',[2220530]),('car_section','C:/Program Files/Altair/2019/tutorials/hm/car_section.hm',[26806,26807])]
for label,fn,expected in files:
    m=decode(fn)
    ref=set()
    for e in m.elements: ref.update(e.nodes)
    node_ids=set(m.nodes.keys())
    unref=[nid for nid in node_ids if nid not in ref]
    resid=[]
    for nid in unref:
        n=m.nodes[nid]
        zeros=sum(1 for v in (n.x,n.y,n.z) if v==0)
        if zeros>=2: resid.append(nid)
    print(label, 'resid=', sorted(resid), ' expected=', expected)