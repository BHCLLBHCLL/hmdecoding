import sys, os, json, multiprocessing as mp
sys.path.insert(0, 'hmdecoder')
from decoder import decode

gt = json.load(open('output/ground_truth/corpus_gt.json'))

def work(path):
    try:
        m = decode(path)
        return (path, len(m.nodes), len(m.elements))
    except Exception as e:
        return (path, 'ERR', str(e))

if __name__ == '__main__':
    paths = [p for p in list(gt) if os.path.exists(p)]
    with mp.get_context('spawn').Pool() as pool:
        results = pool.map(work, paths)
    n_nok = n_eok = n_bad = total = 0
    fails = []
    for path, nc, ec in results:
        total += 1
        if nc == 'ERR':
            fails.append((os.path.basename(path), 'CRASH', 0, 0)); n_bad += 1; continue
        info = gt[path]
        exp_n = info['counts']['nodes']; exp_e = info['counts']['elements']
        if exp_n == 0 or nc == exp_n:
            n_nok += 1
        else:
            fails.append((os.path.basename(path), 'node', nc, exp_n))
        if exp_e == 0 or ec == exp_e:
            n_eok += 1
        else:
            fails.append((os.path.basename(path), 'elem', ec, exp_e))
    print('total=%d node-ok=%d elem-ok=%d (count gate, mp)' % (total, n_nok, n_eok))
    for f in fails:
        print('  X', f)
    print('PASS' if not fails else 'FAIL')
