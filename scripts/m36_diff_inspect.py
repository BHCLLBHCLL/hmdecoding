import sys, json, re, os
from collections import Counter
sys.path.insert(0, 'hmdecoder')
from decoder import decode
gt = json.load(open('output/ground_truth/corpus_gt.json'))
elems_dir = 'output/ground_truth/elems'

def map_outfile(path):
    b = os.path.basename(path)
    pp = os.path.normpath(path).replace('\\\\', '/')
    parent = 'hm'
    for k, p in [('lsdyna', '/interfaces/lsdyna/'),
                 ('abaqus', '/interfaces/abaqus/'),
                 ('samcef', '/interfaces/samcef/')]:
        if p in pp: parent = k
    f2 = os.path.join(elems_dir, parent + '_' + b + '.elems.txt')
    if os.path.exists(f2): return f2
    f1 = os.path.join(elems_dir, b + '.elems.txt')
    if os.path.exists(f1): return f1
    return None

for target in ['truck.hm', 'dummy_positioner.hm', 'seat_deformer.hm',
               'channel_brkt_assem_analysis.hm', 'icw_ex1.hm', 'icw_ex2.hm',
               'seat_start.hm', 'frame_assembly_3.hm']:
    for path in gt:
        if os.path.basename(path) == target:
            break
    ef = map_outfile(path)
    if not ef:
        print(target, ': no oracle'); continue
    m = decode(path)
    dec = {}
    for e in m.elements:
        dec.setdefault(e.id, []).append((e.config, tuple(e.nodes)))
    oracle = {}
    for line in open(ef, encoding='utf-8'):
        mm = re.match(r'E (\d+) cfg=(\d+) nodes=(.*)', line.strip())
        if mm:
            eid = int(mm.group(1)); cfg = int(mm.group(2))
            nds = tuple(x for x in (int(x) for x in mm.group(3).split()) if x != 0)
            oracle[eid] = (cfg, nds)
    diff_cfg = {}
    diff_nodes = []
    for eid, (cfg, nds) in oracle.items():
        if eid not in dec:
            diff_cfg.setdefault('only_oracle', []).append((eid, cfg, nds)); continue
        dcands = [d for d in dec[eid] if d[0] == cfg]
        if dcands:
            if not any(d[1] == nds for d in dcands):
                diff_nodes.append((eid, cfg, nds, dcands[0][1]))
        else:
            diff_cfg.setdefault('cfg_mismatch', []).append((eid, cfg, [d[0] for d in dec[eid]]))
    print('\n===', target, '===')
    print(' cfg_mismatch:', {k: len(v) for k, v in diff_cfg.items()})
    cfgs = Counter(cfg for _, cfg, _, _ in diff_nodes)
    print(' dn by cfg:', dict(cfgs))
    for k in (55, 60, 61, 104, 204):
        if k in cfgs:
            print(' cfg=', k, ' samples:')
            n = 0
            for eid, cfg, ora, dec2 in diff_nodes:
                if cfg == k:
                    print('   eid=', eid, ' oracle_nds=', ora, ' dec_nds=', dec2)
                    n += 1
                    if n >= 3: break