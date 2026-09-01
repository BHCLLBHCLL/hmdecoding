fn='hmdecoder/decoder.py'
d=open(fn,encoding='utf-8').read()
anchor='def _parse_cfg55_mpc'
i=d.index(anchor)
new = '''def _parse_v13c60(p, sh, cnt, row_count, row_map, max_rec=None):
    """v13 Y=1 \u51e0\u4f55\u6bb5 config-60 \u8bb0\u5f55 (\u542b\u6d6e\u70b9\u663e\u793a\u6570\u636e):
    eid = u32@+rec, node1_row = u16@+rec+14, node2_row = u16@+rec+18; stride = 118."""
    elems = {}
    # first record offset: find eid-looking u32 near sh+24..sh+80 with valid coords
    rec = None
    for off in range(sh + 24, min(sh + 120, len(p) - 4)):
        eid = u32(p, off)
        n1 = u16(p, off + 14)
        n2 = u16(p, off + 18)
        if 0 < eid < 10_000_000 and 1 <= n1 <= row_count and 1 <= n2 <= row_count:
            rec = off
            break
    if rec is None:
        return None
    limit = min(cnt, max_rec if max_rec else cnt)
    for k in range(limit):
        if rec + 118 > len(p):
            break
        eid = u32(p, rec)
        n1 = u16(p, rec + 14)
        n2 = u16(p, rec + 18)
        if not (0 < eid < 10_000_000 and 1 <= n1 <= row_count and 1 <= n2 <= row_count):
            break
        _rec_add(elems, eid, 60, [row_map.get(n1, n1), row_map.get(n2, n2)])
        rec += 118
    return elems or None

'''
d = d[:i] + new + d[i:]
open(fn,'w',encoding='utf-8').write(d)
import ast
ast.parse(d)
print('INSERTED _parse_v13c60 SYNTAX OK')