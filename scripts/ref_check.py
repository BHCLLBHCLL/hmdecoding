import sys,os
sys.path.insert(0,'hmdecoder')
from decoder import decode
files=[('seat_2','C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm',[149]),('seat_start','C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_start.hm',[149]),('truck','C:/Program Files/Altair/2019/tutorials/hm/truck.hm',[2220530]),('car_section','C:/Program Files/Altair/2019/tutorials/hm/car_section.hm',[26806,26807])]
for label,fn,expected in files:
    m=decode(fn)
    # collect all node ids referenced by elements
    ref=set()
    for e in m.elements:
        ref.update(e.nodes)
    node_ids=set(m.nodes.keys())
    # find 'referenced' nodes that are NOT in node table (should not happen) and
    unreferenced=[nid for nid in node_ids if nid not in ref]
    print('%s: nodes=%d referenced_in_elements=%d  unreferenced_count=%d'%(label,len(node_ids),len(ref),len(unreferenced)))
    print('   expected_extra=%s'%expected)
    print('   unreferenced_ids=%s'%sorted(unreferenced))