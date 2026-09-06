"""合并 decoder 统计与 oracle 计数, 输出覆盖率缺口分析."""
import json, os, re
from collections import defaultdict

NL = chr(10)
rows = json.load(open('output/sweep4_decode.json', encoding='utf-8'))
bybase = {}
for r in rows:
    bybase[os.path.basename(r['path'])] = r

# 解析 oracle log
ents = ['nodes', 'elems', 'comps', 'mats', 'props', 'loads', 'loadcols', 'systems',
        'groups', 'sets', 'points', 'lines', 'surfs', 'solids', 'titles']
oracle = {}  # basename -> dict ent->count
readerr = {}
with open('output/sweep4_oracle.log', encoding='utf-8', errors='replace') as fh:
    for line in fh:
        line = line.rstrip()
        if not line.startswith('== '):
            continue
        parts = line.split(' | ')
        if parts[1] == 'READ-ERR':
            readerr[parts[0].split('== ')[1]] = parts[2][:120] if len(parts) > 2 else '?'
            continue
        bname = parts[0].split('== ')[1]
        d = {}
        for p in parts[2:]:
            m = re.match(r'([a-z]+)=(-?[0-9]+)', p)
            if m:
                d[m.group(1)] = int(m.group(2))
        oracle[bname] = d

print('decoder files:', len(rows), ' oracle files:', len(oracle), ' read-err:', len(readerr))

# 合并统计
matched = 0
mismatch_node = []
mismatch_elem = []
dec_crash = [r for r in rows if 'crash' in r]
zero_node = [r for r in rows if 'crash' not in r and r['nodes'] == 0]

# decoder 缺失的实体: oracle 计数>0 而 decoder 无对应字段
missing_ents = defaultdict(list)  # ent -> [basenames]
ent_present_files = defaultdict(int)  # ent -> 文件数(oracle>0)
for bname, od in oracle.items():
    r = bybase.get(bname)
    if r is None or 'crash' in r:
        continue
    matched += 1
    # 节点/单元对照
    if od.get('nodes', -1) >= 0 and od['nodes'] != r['nodes']:
        mismatch_node.append((bname, r['nodes'], od['nodes'], r['db']))
    if od.get('elems', -1) >= 0 and od['elems'] != r['elems']:
        mismatch_elem.append((bname, r['elems'], od['elems'], r['db']))
    # decoder 未解码实体 (oracle>0)
    for ent in ['loads', 'loadcols', 'systems', 'sets', 'points', 'lines', 'surfs', 'solids', 'titles']:
        if od.get(ent, 0) > 0:
            ent_present_files[ent] += 1
            if ent == 'points':
                if len(r.get('display_points', {})) + len(r.get('geo_points', {})) == 0:
                    missing_ents[ent].append(bname)
            else:
                missing_ents[ent].append(bname)

print(NL + '=== 节点/单元对照 (decoder vs oracle) ===')
print('matched files:', matched)
print('node mismatch:', len(mismatch_node))
for b, dv, ov, db in mismatch_node[:15]:
    print('  NODE-MISMATCH %s dec=%d ora=%d (db %.2f)' % (b, dv, ov, db))
print('elem mismatch:', len(mismatch_elem))
for b, dv, ov, db in mismatch_elem[:15]:
    print('  ELEM-MISMATCH %s dec=%d ora=%d (db %.2f)' % (b, dv, ov, db))
print('decoder crash:', len(dec_crash))
for r in dec_crash[:15]:
    print('  CRASH %s %s' % (r['path'], r['crash'][:100]))
print('decoder zero-node:', len(zero_node))

print(NL + '=== decoder 缺失实体 (oracle>0 且 decoder 未解) ===')
for ent in ['loads', 'loadcols', 'systems', 'sets', 'points', 'lines', 'surfs', 'solids', 'titles']:
    ms = missing_ents.get(ent, [])
    print('%s: oracle>0 文件数=%d, decoder 全缺=%d' % (ent, ent_present_files.get(ent, 0), len(ms)))
    if ms and len(ms) <= 12:
        print('   e.g.', ', '.join(ms[:8]))

# comps/mats/props/groups 对照
for ent, key in [('comps', 'comps'), ('mats', 'mats'), ('props', 'props'), ('groups', 'groups')]:
    mm = []
    for bname, od in oracle.items():
        r = bybase.get(bname)
        if r is None or 'crash' in r:
            continue
        if od.get(ent, -1) >= 0 and od[ent] != r[key]:
            mm.append((bname, r[key], od[ent]))
    print('%s mismatch: %d' % (ent, len(mm)))
    for b, dv, ov in mm[:10]:
        print('  %s-MISMATCH %s dec=%d ora=%d' % (ent.upper(), b, dv, ov))

# db 版本分布
from collections import Counter
dbc = Counter(round(r['db'], 2) for r in rows if 'crash' not in r)
print(NL + '=== db 版本分布 (decoder) ===')
for v, n in sorted(dbc.items()):
    print('  %.2f  %d' % (v, n))
