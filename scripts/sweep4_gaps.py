"""按 db 版本归组解码缺口."""
import json, os, re
from collections import defaultdict

rows = json.load(open('output/sweep4_decode.json', encoding='utf-8'))
oracle = {}
for line in open('output/sweep4_oracle.log', encoding='utf-8', errors='replace'):
    line = line.rstrip()
    if not line.startswith('== '): continue
    parts = line.split(' | ')
    if parts[1] == 'READ-ERR': continue
    bname = parts[0].split('== ')[1]
    d = {}
    for p in parts[2:]:
        m = re.match(r'([a-z]+)=(-?[0-9]+)', p)
        if m: d[m.group(1)] = int(m.group(2))
    oracle[bname] = d

byver = defaultdict(lambda: [0,0,0])  # db -> [files, node_ok, elem_ok]
zn_byver = defaultdict(list)          # db -> zero-node basenames (oracle has nodes)
em_byver = defaultdict(list)          # db -> elem-mismatch basenames
for r in rows:
    b = os.path.basename(r['path'])
    if 'crash' in r: continue
    v = round(r['db'], 2)
    byver[v][0] += 1
    od = oracle.get(b)
    if od is None: continue
    if od.get('nodes', 0) == 0:
        byver[v][1] += 1  # oracle 无节点, 算 ok
    elif r['nodes'] == od['nodes']:
        byver[v][1] += 1
    else:
        if r['nodes'] == 0:
            zn_byver[v].append(b)
    if od.get('elems', 0) == 0 or r['elems'] == od['elems']:
        byver[v][2] += 1
    else:
        em_byver[v].append(b)

print('=== 按 db 版本: 文件数 / 节点完全命中(含 oracle=0) / 单元完全命中 ===')
for v in sorted(byver):
    f, nok, eok = byver[v]
    print('  %5.2f  files=%3d  node-ok=%3d  elem-ok=%3d' % (v, f, nok, eok))

print()
print('=== 零节点失败文件 (oracle 有节点但 dec=0) 按版本 ===')
for v in sorted(zn_byver):
    print('  %5.2f (%d): %s' % (v, len(zn_byver[v]), ', '.join(sorted(zn_byver[v])[:12])))

print()
print('=== 单元不符文件 (dec<ora) 按版本 ===')
for v in sorted(em_byver):
    print('  %5.2f (%d): %s' % (v, len(em_byver[v]), ', '.join(sorted(em_byver[v])[:14])))
