import glob, os, re
base = "C:/Program Files/Altair/2019/help/hm"
files = glob.glob(base + "/**/*.htm*", recursive=True)
print("hm help files:", len(files))
# 分类
cats = {}
for f in files:
    d = os.path.dirname(f).replace("\\", "/").split("/")[-1]
    cats[d] = cats.get(d, 0) + 1
print("subdirs:", sorted(cats.items(), key=lambda x: -x[1])[:15])
# 搜索格式相关关键词
kw = re.compile(r"(hmascii|\bhm\s+file\b|binary\s+format|file\s+format|database\s+format)", re.I)
hits = []
for f in files:
    try:
        data = open(f, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue
    if kw.search(data):
        hits.append(f)
print("format-related files:", len(hits))
for h in hits[:20]:
    print("  ", h.split("hm/")[-1])
