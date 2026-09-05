import sys, os, re, json
sys.path.insert(0, 'hmdecoder')
from decoder import decode

LOG = 'output/ground_truth/nc_all.log'

def parse_log(path):
    oracle = {}
    cur = None
    for line in open(path, encoding='utf-8'):
        line = line.strip()
        if line.startswith('==FILE== '):
            cur = line.split('==FILE== ', 1)[1]
            oracle[cur] = {}
        elif line.startswith('N '):
            p = line.split()
            # N <id> <x> <y> <z>  (可能负号/科学计数)
            if len(p) >= 5:
                oracle[cur][int(p[1])] = (float(p[2]), float(p[3]), float(p[4]))
        elif line.startswith('NCOUNT '):
            pass
    return oracle

def compare_one(path, ocoords, tol=1e-4):
    try:
        m = decode(path)
    except Exception as e:
        return ('ERR', str(e), 0, 0, 0, 0)
    nodes = m.nodes
    ok = mism = only_dec = only_ora = 0
    for nid, (ox, oy, oz) in ocoords.items():
        nd = nodes.get(nid)
        if nd is None:
            only_ora += 1
            continue
        if (abs(nd.x - ox) <= tol and abs(nd.y - oy) <= tol and abs(nd.z - oz) <= tol):
            ok += 1
        else:
            mism += 1
            if mism <= 3:
                print('    nid %d ora=(%g,%g,%g) dec=(%g,%g,%g)' % (nid, ox, oy, oz, nd.x, nd.y, nd.z))
    for nid in nodes:
        if nid not in ocoords:
            only_dec += 1
    return ('OK', '', ok, mism, only_dec, only_ora), len(ocoords)

if __name__ == '__main__':
    oracle = parse_log(LOG)
    print('harvested files:', len(oracle))
    # 按文件输出 (仅对已harvest且解码快的子集)
    tot_ok = tot_mism = tot_dec = tot_ora = 0
    for path, ocoords in oracle.items():
        if not ocoords:
            continue
        res, oc = compare_one(path, ocoords)
        tag, err, ok, mism, od, oo = res
        if tag == 'ERR':
            print('  %s: ERR %s' % (path, err)); continue
        tot_ok += ok; tot_mism += mism; tot_dec += od; tot_ora += oo
        status = 'OK' if (mism == 0 and od == 0 and oo == 0) else 'DIFF'
        print('  %-55s coords=%d ok=%d mism=%d od=%d oo=%d -> %s' % (os.path.basename(path), oc, ok, mism, od, oo, status))
    print('TOTAL ok=%d mism=%d od=%d oo=%d' % (tot_ok, tot_mism, tot_dec, tot_ora))
