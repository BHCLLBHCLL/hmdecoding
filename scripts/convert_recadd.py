import re
p = "hmdecoder/decoder.py"
src = open(p, encoding="utf-8").read()
# helper injection after u32 def
helper = '''
def _rec_add(elems, eid, cfg, nds):
    """保留同 eid 的重复记录 (car_section 等 Ansys 多实体模型). dict[eid]=list[(cfg, nds)]."""
    elems.setdefault(eid, []).append((cfg, nds))
    return elems
'''
if "def _rec_add" not in src:
    src = src.replace('def u32(p, o): return struct.unpack_from("<I", p, o)[0]',
                      'def u32(p, o): return struct.unpack_from("<I", p, o)[0]' + helper, 1)
# convert each matching single line
out = []
cnt = 0
for ln in src.split("\n"):
    m = re.match(r"^(\s*)elems\[eid\] = \(([^,]+), (\[[^\]]*\])\)\s*$", ln)
    if m:
        cnt += 1
        ind, cfg, rows = m.group(1), m.group(2), m.group(3)
        out.append(f"{ind}_rec_add(elems, eid, {cfg}, {rows})")
    else:
        out.append(ln)
src = "\n".join(out)
# fix not-in-elems guards (allow duplicates)
src = src.replace("if eid not in elems and 0 < eid < 10_000_000:", "if 0 < eid < 10_000_000:")
src = src.replace("if eid not in elems and 0 < eid < 10_000_000 and len(rows) == 4:", "if 0 < eid < 10_000_000 and len(rows) == 4:")
# decode_elements records.extend for list values
src = src.replace("records.extend((eid, cfg, nds) for eid, (cfg, nds) in got.items())",
                  "records.extend((eid, cfg, nds) for eid, recs in got.items() for (cfg, nds) in recs)")
open(p, "w", encoding="utf-8").write(src)
print("converted lines:", cnt)
import ast; ast.parse(src); print("syntax ok")
