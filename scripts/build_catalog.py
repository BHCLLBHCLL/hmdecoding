import os, re, json, html

PDIR = r'C:/Program Files/Altair/2019/help/hm/topics/panels'

def clean(text):
    text = re.sub(r'<[^>]+>', ' ', text)
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_title(fname):
    c = open(os.path.join(PDIR, fname), encoding='utf-8', errors='ignore').read()
    t = re.search(r'<title>([^<]*)</title>', c)
    name = t.group(1).strip() if t else ''
    name = re.sub(r'\s*Panel\s*$', '', name)  # 去 "Panel" 后缀
    body = re.search(r'<body[^>]*>(.*)</body>', c, re.S)
    bodytext = clean(body.group(1)) if body else ''
    return name, bodytext

# 收集所有 help###.htm
files = sorted(f for f in os.listdir(PDIR) if re.match(r'help\d+\.htm$', f))
print('help%%d files:', len(files))
panels = {}
for f in files:
    try:
        name, bodytext = extract_title(f)
    except Exception:
        continue
    if not name:
        continue
    # 正文里可能含按钮/输入名; 提取首 600 字符作为摘要
    summary = bodytext[:600]
    panels[name] = {'help_page': f, 'summary': summary, 'status': 'missing'}

json.dump({'panels': panels, 'count': len(panels)}, open(r'D:/training/caedecoder/hmdecoding/catalog.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('catalog.json written, panels:', len(panels))
# 打印前 20 个名字
for i, (name, info) in enumerate(panels.items()):
    if i < 20:
        print('  %s -> %s' % (name, info['help_page']))
