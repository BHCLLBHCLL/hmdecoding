fn='hmdecoder/decoder.py'
d=open(fn,encoding='utf-8').read()
i=d.index('def _parse_cfg55_mpc')
j=d.index('def decode_elements')
ESC="\\xf5\\x1f"
new = '''def _parse_cfg55_mpc(p, sh, cnt, row_count, row_map, max_rec=None):
    """Family-1 family record (config 22/55): [CONST][storage][?][?][eid@+18][0][0][flag]
    eid = u16@+18; config = u16@+30 - 512."""
    s = None
    for off in range(sh + 16, min(sh + 80, len(p) - 4)):
        if is_const(u32(p, off)):
            s = off
            break
    if s is None:
        return None
    elems = {}
    rec = s
    limit = min(cnt, max_rec if max_rec else cnt)
    for k in range(limit):
        if not is_const(u32(p, rec)):
            nxt = None
            j = p.find(b"'''+ESC+'''", rec + 4, min(rec + 200, len(p) - 2))
            while j >= 0:
                if is_const(u32(p, j)):
                    nxt = j
                    break
                j = p.find(b"'''+ESC+'''", j + 1, min(rec + 200, len(p) - 2))
            if nxt is None:
                break
            rec = nxt
        eid = u16(p, rec + 18)
        cfg = u16(p, rec + 30) - 512
        if not (0 < eid < 10_000_000):
            break
        if cfg == 55:
            nslave = u32(p, rec + 32)
            master = u32(p, rec + 36)
            if not (1 <= master <= row_count and 0 <= nslave <= 60):
                break
            slaves = []
            for t in range(nslave):
                r = u32(p, rec + 48 + 4 * t)
                if not (1 <= r <= row_count):
                    break
                slaves.append(r)
            if len(slaves) != nslave:
                break
            nds = [master] + slaves
            tail = rec + 48 + 4 * nslave
        else:
            ncfg = 0
            while ncfg < 20 and rec + 32 + 4 * ncfg + 4 <= len(p):
                r = u32(p, rec + 32 + 4 * ncfg)
                if not (1 <= r <= row_count):
                    break
                ncfg += 1
            if ncfg < 1:
                break
            nds = [u32(p, rec + 32 + 4 * t) for t in range(ncfg)]
            tail = rec + 32 + 4 * ncfg
        _rec_add(elems, eid, cfg, [row_map.get(r, r) for r in nds])
        nxt = None
        j = p.find(b"'''+ESC+'''", tail, min(tail + 120, len(p) - 2))
        while j >= 0:
            if is_const(u32(p, j)):
                nxt = j
                break
            j = p.find(b"'''+ESC+'''", j + 1, min(tail + 120, len(p) - 2))
        if nxt is None:
            break
        rec = nxt
    return elems or None

'''.replace('%ESC%', ESC)
d = d[:i] + new + d[j:]
open(fn,'w',encoding='utf-8').write(d)
import ast
ast.parse(d)
print('SPLICED SYNTAX OK')