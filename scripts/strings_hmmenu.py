import re
b = open(r'C:/Program Files/Altair/2019/hm/bin/win64/hmmenu.set', 'rb').read()
# 提取长度 >=4 的 ASCII 串
strs = re.findall(rb'[\x20-\x7e]{4,}', b)
dec = [s.decode('ascii') for s in strs]
import collections
print('total strings:', len(dec))
# 找常见菜单名 (顶部菜单)
menus = ['File','Edit','View','Collectors','Geometry','Mesh','Connectors','Materials','Properties','BCs','Setup','Tools','Morphing','Post','XYPlots','Preferences','Applications','Help']
found = [m for m in menus if any(m.lower() in d.lower() for d in dec)]
print('top menus present:', found)
# 前 40 个非数字串
shown = 0
for d in dec:
    if len(d) >= 5 and not d.isdigit():
        if shown < 30:
            print(repr(d))
            shown += 1
