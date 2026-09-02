import sys,re
sys.path.insert(0,'hmdecoder')
from decoder import decode
m=decode('C:/Program Files/Altair/2019/tutorials/hm/interfaces/samcef/hook.hm')
dec=set(e.id for e in m.elements)
oracle=set()
for line in open('output/ground_truth/hook_elems_all.txt',encoding='utf-8'):
    mm=re.match(r'E (\d+) cfg=(\d+) nodes=(.*)',line.strip())
    if mm: oracle.add(int(mm.group(1)))
print('only_ora:', sorted(oracle-dec))
print('only_dec:', sorted(dec-oracle))