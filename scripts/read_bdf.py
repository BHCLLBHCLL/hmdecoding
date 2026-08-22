import re
data = open("output/ground_truth/ws_nastran.bdf", encoding="ascii", errors="replace").read()
cards = re.findall(r"^(CTETRA|CHEXA|CPENTA|CTRIA3|CQUAD4|CTRIA6|CQUAD8|CBAR|CROD|GRID)\s+\S+", data, re.M)
from collections import Counter
print(Counter(cards))
# sample lines
lines = [l for l in data.splitlines() if l.strip().startswith(("CTETRA", "CQUAD4", "CTRIA3"))][:6]
for l in lines:
    print(l)
print("file size:", len(data))
