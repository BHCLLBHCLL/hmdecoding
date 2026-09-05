import re, glob, os, json
macs = glob.glob(r'C:/Program Files/Altair/2019/hm/bin/win64/*.mac')
macros = {}
for mf in macs:
    bn = os.path.basename(mf)
    txt = open(mf, encoding='utf-8', errors='ignore').read()
    pat = re.compile(r'\*createbutton\(\s*([0-9]+)\s*,\s*"([^"]+)"\s*,\s*(-?[0-9]+)\s*,\s*(-?[0-9]+)\s*,\s*([0-9]+)\s*,\s*([A-Za-z_]+)\s*,\s*"([^"]*)"', re.S)
    cnt = 0
    for m in pat.finditer(txt):
        page, label, row, col, size, kind, tip = m.groups()
        macros.setdefault(bn, []).append({'page': int(page), 'label': label, 'row': int(row), 'col': int(col), 'kind': kind, 'tip': tip})
        cnt += 1
    if cnt:
        print('%s: %d macros' % (bn, cnt))
    for b in macros.get(bn, [])[:5]:
        print('   page%s [%s] label=%s pos=(%d,%d) tip=%s' % (b['page'], b['kind'], b['label'], b['row'], b['col'], b['tip'][:40]))
cur = json.load(open(r'D:/training/caedecoder/hmdecoding/catalog.json', encoding='utf-8'))
cur['macros'] = macros
cur['macro_files'] = list(macros.keys())
json.dump(cur, open(r'D:/training/caedecoder/hmdecoding/catalog.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('catalog updated with macros, files:', len(macros))
