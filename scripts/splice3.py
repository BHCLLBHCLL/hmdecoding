fn='hmdecoder/decoder.py'
d=open(fn,encoding='utf-8').read()
old = '        if eid is None or cfg is None or nds is None or tail is None:\n            break'
new = '        if eid is None or cfg is None or nds is None or tail is None:\n            # unrecognized CONST anchor (e.g. v12 0x70501FF5 split): skip to next CONST and continue\n            skip = None\n            jj = p.find(b"[XF5]"); '.replace('[XF5]','\\xf5\\x1f') + '", rec + 4, min(rec + 200, len(p) - 2))\n            while jj >= 0:\n                if is_const(u32(p, jj)):\n                    skip = jj\n                    break\n                jj = p.find(b"\\xf5\\x1f", jj + 1, min(rec + 200, len(p) - 2))\n            if skip is None:\n                break\n            rec = skip\n            continue'
assert old in d, 'old not found'
d=d.replace(old,new)
open(fn,'w',encoding='utf-8').write(d)
import ast; ast.parse(d)
print('SKIP-FIX SPLICED SYNTAX OK')