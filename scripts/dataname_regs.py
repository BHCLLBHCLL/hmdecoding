import glob, re, collections
base = "C:/Program Files/Altair/2019/hm/scripts"
files = glob.glob(base + "/**/*.tcl", recursive=True)
pat = re.compile(r"hm_registertooltipforentitydataname\s+[^\n]*", re.I)
regs = collections.Counter()
samples = {}
for f in files:
    try:
        data = open(f, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue
    for m in pat.finditer(data):
        line = m.group().strip()
        # 提取实体类型和 dataname（启发式）
        parts = line.split()
        key = " ".join(parts[:4])
        regs[key] += 1
        samples.setdefault(key, line)
out = []
out.append(f"dataname 注册模式: {len(regs)} 种")
for k, n in regs.most_common(30):
    out.append(f"  {n:5d}x  {k[:90]}")
open("output/ground_truth/dataname_regs.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
