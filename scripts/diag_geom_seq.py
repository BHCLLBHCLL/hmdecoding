import re
lines = open('output/ground_truth/harvest.log', encoding='utf-8', errors='replace').read().splitlines()
start = None
for idx, l in enumerate(lines):
    if l.startswith('==FILE== ') and 'geometry.hm' in l:
        start = idx
        break
c = []
for l in lines[start:]:
    m = re.match(r'^elem id=\d+ config=(\d+)$', l)
    if m:
        c.append(int(m.group(1)))
    elif c and not l.startswith('elem'):
        # stop at next file or non-elem after data started
        if l.startswith('==FILE=='):
            break
print('total', len(c))
print('hist', {x: c.count(x) for x in sorted(set(c))})
print('config103 eids:', [k + 1 for k in range(len(c)) if c[k] == 103])
trans = [(k + 1, c[k]) for k in range(1, len(c)) if c[k] != c[k - 1]]
print('num transitions', len(trans))
print('first 20 transitions:', trans[:20])
print('last 5 transitions:', trans[-5:])
