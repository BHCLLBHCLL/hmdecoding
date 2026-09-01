import sys,os
sys.path.insert(0,'hmdecoder')
from decoder import decode
for fn,label,ids in [('C:/Program Files/Altair/2019/tutorials/hm/icw_ex2.hm','icw_ex2',[91,93]),('C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm','seat_2',[149]),('C:/Program Files/Altair/2019/tutorials/hm/body_side_assembly.hm','body_side',[58551])]:
    m=decode(fn)
    ref=set()
    for e in m.elements: ref.update(e.nodes)
    for nid in ids:
        n=m.nodes.get(nid)
        if n:
            zeros=sum(1 for c_ in (n.x,n.y,n.z) if c_==0)
            print('%s nid=%d x=%g y=%g z=%g zero=%d in_ref=%s'%(label,nid,n.x,n.y,n.z,zeros,nid in ref))
        else:
            print('%s nid=%d NOT_IN_NODES'%(label,nid))