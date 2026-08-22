import re
data = open("C:/Program Files/Altair/2019/hm/scripts/hypermesh.tcl", encoding="utf-8", errors="ignore").read()
lines = data.splitlines()
out = []
for i, ln in enumerate(lines):
    if re.search(r"hmascii|ascii", ln, re.I):
        lo = max(0, i - 3); hi = min(len(lines), i + 3)
        for j in range(lo, hi):
            out.append(f"{j:5d}: {lines[j][:120]}")
        out.append("---")
open("output/ground_truth/hm_ascii_ctx.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
