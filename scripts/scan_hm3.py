import glob, os, re
# 1. 全安装目录找 PDF 手册
pdfs = glob.glob("C:/Program Files/Altair/2019/**/*.pdf", recursive=True)
print("PDFs:", len(pdfs))
for p in pdfs[:20]:
    print("  ", p)
# 2. 帮助里搜 Tcl 参考关键词
import json
base = "C:/Program Files/Altair/2019/help/hm"
files = glob.glob(base + "/**/*.htm*", recursive=True)
tcl_ref = []
for f in files:
    try:
        data = open(f, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue
    if "hm_getvalue" in data or "hm_createmark" in data or "hm_getmark" in data:
        tcl_ref.append(f)
print("Tcl API pages:", len(tcl_ref))
for t in tcl_ref[:10]:
    print("  ", t.split("hm/")[-1])
