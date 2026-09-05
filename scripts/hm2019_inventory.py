#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 Altair 2019 help 抽取 HyperMesh 官方 UI 清单."""
import re
from pathlib import Path

HELP = Path(r"C:/Program Files/Altair/2019/help/hm/topics")

# Panels TOC: help042.htm">Accels Panel
pat_panel = re.compile(
    r'topics/panels/help[^"]+\.htm">([^<]+Panel)</a>', re.I)
# also quality index secondary etc
pat_panel2 = re.compile(
    r'topics/panels/[^"]+\.htm">([^<]+)</a>')

text = (HELP / "panels" / "panels_r.htm").read_text(encoding="utf-8", errors="ignore")
# Only the expanded TOC under Panels (first big list)
# Extract unique "Xxx Panel" titles from the publication TOC section
names = []
seen = set()
for m in pat_panel.finditer(text):
    n = re.sub(r"\s+", " ", m.group(1)).strip()
    if n.lower() not in seen and n != "Panels":
        seen.add(n.lower())
        names.append(n)

print(f"OFFICIAL_PANELS={len(names)}")
for n in names:
    print("P|", n)

# Browsers
btext = (HELP / "user_interface" / "browsers_r.htm").read_text(
    encoding="utf-8", errors="ignore")
# leaf titles that end with Browser
browsers = []
for m in re.finditer(r'class="title"><a href="[^"]+">([^<]*Browser[^<]*)</a>', btext):
    n = re.sub(r"\s+", " ", m.group(1)).strip()
    if n.lower() not in {x.lower() for x in browsers}:
        browsers.append(n)
print(f"OFFICIAL_BROWSERS={len(browsers)}")
for n in browsers:
    print("B|", n)

# Toolbars page: look for toolbar names
ttext = (HELP / "user_interface" / "toolbars_r.htm").read_text(
    encoding="utf-8", errors="ignore")
toolbars = []
for m in re.finditer(r'class="title"><a href="[^"]+">([^<]*Toolbar[^<]*)</a>', ttext):
    n = re.sub(r"\s+", " ", m.group(1)).strip()
    if n.lower() not in {x.lower() for x in toolbars}:
        toolbars.append(n)
print(f"OFFICIAL_TOOLBARS={len(toolbars)}")
for n in toolbars:
    print("T|", n)

# Visualization controls
vtext = (HELP / "user_interface" / "visualization_controls_r.htm").read_text(
    encoding="utf-8", errors="ignore")
viz = []
for m in re.finditer(r'class="title"><a href="[^"]+">([^<]+)</a>', vtext):
    n = re.sub(r"\s+", " ", m.group(1)).strip()
    if "visual" in n.lower() or "view" in n.lower() or "display" in n.lower():
        if n.lower() not in {x.lower() for x in viz}:
            viz.append(n)
print(f"VIZ={len(viz)}")
for n in viz[:40]:
    print("V|", n)
