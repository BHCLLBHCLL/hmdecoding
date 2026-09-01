fn='hmdecoder/decoder.py'
d=open(fn,encoding='utf-8').read()
i=d.index('def _parse_cfg55_mpc')
j=d.index('def decode_elements')
ESC="\\xf5\\x1f"
new = '''def _parse_cfg55_mpc(p, sh, cnt, row_count, row_map, max_rec=None):
    """Family-1 family record (config 22/55), attempts candidate layouts and validates.
    eid: u16@+18 (if valid & non-zero) else u32@+4.
    config: u16@+30-512 (seat v11) or u16@+22&0xFF (v12).
    Node layout: master+slave (nslave@+32,master@+36,slv@+48 | nslave@+24,master@+28,slv@+40)
                 or fixed node sequence (@+32 / @+24)."""
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
        const = u32(p, rec)
        eid = None; cfg = None; nds = None; tail = None
        if (const >> 16) in (0x7024, 0x7054, 0x7050):
            e18 = u16(p, rec + 18)
            e4 = u32(p, rec + 4)
            e = e18 if (0 < e18 < 10_000_000 and e18 != e4 and e4 < 100000) else e4
            c30 = u16(p, rec + 30) - 512
            c22 = u16(p, rec + 22) & 0xFF
            # candidate configs & layouts
            cands = []
            for cc, tag in ((c30,'30'), (c22,'22')):
                if not (1 <= cc <= 100):
                    continue
                if cc == 55:
                    # (nslave,master,slvoff): try @+24/@+28/@+40 then @+32/@+36/@+48
                    for (nso,mo,svo) in ((24,28,40),(32,36,48)):
                        nsl = u32(p, rec + nso)
                        master = u32(p, rec + mo)
                        if 1 <= master <= row_count and 0 <= nsl <= 2000 and rec + svo + 4*nsl + 4 <= len(p):
                            sl = [u32(p, rec + svo + 4 * t) for t in range(nsl)]
                            if all(1 <= r <= row_count for r in sl):
                                cands.append((cc, [master]+sl, rec + svo + 4 * nsl))
                                break
                else:
                    # fixed node sequence: try @+24 then @+32, until 0/out-of-range
                    for no in (24,32):
                        nn = 0
                        while nn < 20 and rec + no + 4*nn + 4 <= len(p):
                            r = u32(p, rec + no + 4 * nn)
                            if r == 0 or not (1 <= r <= row_count):
                                break
                            nn += 1
                        if nn >= 1:
                            cands.append((cc, [u32(p, rec + no + 4 * t) for t in range(nn)], rec + no + 4 * nn))
                            break
            for (cc, nd, tl) in cands:
                if 0 < e < 10_000_000:
                    eid, cfg, nds, tail = e, cc, nd, tl
                    break
        if eid is None or cfg is None or nds is None or tail is None:
            skip = None
            jj = p.find(b"'''+ESC+'''", rec + 4, min(rec + 200, len(p) - 2))
            while jj >= 0:
                if is_const(u32(p, jj)):
                    skip = jj
                    break
                jj = p.find(b"'''+ESC+'''", jj + 1, min(rec + 200, len(p) - 2))
            if skip is None:
                break
            rec = skip
            continue
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

'''
d = d[:i] + new + d[j:]
open(fn,'w',encoding='utf-8').write(d)
import ast
ast.parse(d)
print('SPLICED SYNTAX OK')