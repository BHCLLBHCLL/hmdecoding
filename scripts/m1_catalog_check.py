import re, json, sys
sys.path.insert(0, '.')

# 1. 从 hm_gui.py 提取 HM_PANEL_PAGES 与 implemented 集合
src = open('hm_gui.py', encoding='utf-8').read()
mpages = re.search(r'HM_PANEL_PAGES\s*=\s*(\{.*?\n\})', src, re.S)
import ast
pages = ast.literal_eval(mpages.group(1))
gui_buttons = [name.strip() for col in pages.values() for row in col for name in row]
# implemented
impl_src = re.search(r'implemented = \{(.*?)\}', src, re.S).group(1)
impl = set(re.findall(r'\"([^\"]+)\"\s*:', impl_src))
print('GUI pages:', list(pages.keys()))
print('GUI buttons:', len(gui_buttons), 'implemented:', len(impl))

# 2. 官方 catalog
cat = json.load(open('catalog.json', encoding='utf-8'))
official = set(cat['panels'].keys())
lower_official = {k.lower() for k in official}

# 3. 交叉校验: GUI 按钮在所有官方面板中出现?
missing_official = []
for b in gui_buttons:
    if b.lower() not in lower_official:
        missing_official.append(b)
print('GUI buttons NOT in official catalog:', missing_official)

# 4. 官方面板中 GUI 未覆盖的 (前 30)
gui_lower = {b.lower() for b in gui_buttons}
uncovered = [o for o in sorted(official) if o.lower() not in gui_lower]
print('official panels not in GUI (of %d): %d' % (len(official), len(uncovered)))
for u in uncovered[:25]:
    print('   -', u)
print('--- PASS if missing_official is empty and impl>=14')
