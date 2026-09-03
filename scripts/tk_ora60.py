import re
for line in open('output/ground_truth/elems/truck.hm.elems.txt',encoding='utf-8'):
    mm=re.match(r'E (220195|2123800) cfg=(\d+) nodes=(.*)',line.strip())
    if mm:
        print('oracle',mm.group(1),'cfg',mm.group(2),'nodes',mm.group(3))