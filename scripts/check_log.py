import re
lines = open("output/ground_truth/harvest.log", encoding="utf-8", errors="replace").read().splitlines()
for i, ln in enumerate(lines):
    if "Crank" in ln:
        for j in range(max(0, i - 6), min(len(lines), i + 4)):
            print(f"{j:6d} |{lines[j]!r}")
        print("---")
