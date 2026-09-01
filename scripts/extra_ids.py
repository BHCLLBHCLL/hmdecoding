import sys
sys.path.insert(0,'hmdecoder')
from decoder import decode
for fn,label,gtpath in [('C:/Program Files/Altair/2019/tutorials/hm/car_section.hm','car_section','output/ground_truth/car_nodes_all.txt'),('C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm','seat_2','output/ground_truth/seat_nodes_all.txt')]:
    m=decode(fn)
    dec=set(m.nodes.keys())
    oracle=set(int(x.strip()) for x in open(gtpath,encoding='utf-8') if x.strip().isdigit())
    extra=sorted(dec-oracle)
    missing=sorted(oracle-dec)
    print('%s: extra=%s missing=%s'%(label,extra,missing))