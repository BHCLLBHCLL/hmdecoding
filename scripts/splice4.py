fn='hmdecoder/decoder.py'
d=open(fn,encoding='utf-8').read()
i=d.index('def _parse_cfg55_mpc')
j=d.index('def decode_elements')
ESC="\\xf5\\x1f"
new = '''def _parse_cfg55_mpc(p, sh, cnt, row_count, row_map, max_rec=None):
    """Family-1 family record (config 22/55), v11 + v12 variants.
    Unify: eid (u32@+4 or u16@+18), config = u16@+22&0xFF or u16@+30-512.
    Node layout depends on variant (fixed seq / master+slave)."""
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
        if (const >> 16) in (0x7024, 0x7054):
            # v12: eid@+4, config = u16@+22 & 0xFF
            e = u32(p, rec + 4)
            cc = u16(p, rec + 22) & 0xFF
            # try config-55 master+slave: [nslave][master][1][123456][slave...]
            if cc == 55:
                nsl = u32(p, rec + 24)
                master = u32(p, rec + 28)
                if 1 <= master <= row_count and 1 <= nsl <= 1000 and rec + 40 + 4*nsl + 4 <= len(p):
                    sl = [u32(p, rec + 40 + 4 * t) for t in range(nsl)]
                    if all(1 <= r <= row_count for r in sl):
                        eid, cfg, nds, tail = e, cc, [master]+sl, rec + 40 + 4 * nsl
                if eid is None and u32(p, rec + 24) == 1 and u16(p, rec + 12) == 2596:
                    # hook-style: ncount=u32@+24? fallback master-first @+40
                    ncount = 0
                    while ncount < 2000 and rec + 40 + 4*ncount + 4 <= len(p) and u32(p, rec + 40 + 4*ncount) != 0:
                        ncount += 1
                    ns = [u32(p, rec + 40 + 4 * t) for t in range(ncount)]
                    if ns and all(1 <= r <= row_count for r in ns):
                        eid, cfg, nds, tail = e, cc, ns, rec + 40 + 4 * ncount
            elif (cc in (5, 22)) or 1 <= cc <= 100:
                # fixed sequence @+24,+4 until 0/out-of-range (config 5/22 etc)
                ncfg = 0
                while ncfg < 20 and rec + 24 + 4*ncfg + 4 <= len(p) and u32(p, rec + 24 + 4*ncfg) != 0:
                    r = u32(p, rec + 24 + 4 * ncfg)
                    if not (1 <= r <= row_count):
                        break
                    ncfg += 1
                if ncfg >= 1 and 0 < e < 10_000_000:
                    eid, cfg, nds, tail = e, cc, [u32(p, rec + 24 + 4 * t) for t in range(ncfg)], rec + 24 + 4 * ncfg
        elif (const >> 16) == 0x7024:
            # seat-style (v11): eid=u16@+18, cfg=u16@+30-512
            e = u16(p, rec + 18)
            cc = u16(p, rec + 30) - 512
            if cc == 55:
                nslave = u32(p, rec + 32)
                master = u32(p, rec + 36)
                if 0 < e < 10_000_000 and 1 <= master <= row_count and 0 <= nslave <= 60:
                    slaves = [u32(p, rec + 48 + 4 * t) for t in range(nslave)]
                    if all(1 <= r <= row_count for r in slaves):
                        eid, cfg, nds, tail = e, cc, [master]+slaves, rec + 48 + 4 * nslave
            else:
                ncfg = 0
                while ncfg < 20 and rec + 32 + 4 * ncfg + 4 <= len(p):
                    r = u32(p, rec + 32 + 4 * ncfg)
                    if not (1 <= r <= row_count):
                        break
                    ncfg += 1
                if 0 < e < 10_000_000 and ncfg >= 1 and 1 <= cc <= 100:
                    eid, cfg, nds, tail = e, cc, [u32(p, rec + 32 + 4 * t) for t in range(ncfg)], rec + 32 + 4 * ncfg
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