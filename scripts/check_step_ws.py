import re
data = open("output/real_inp/ws_tetra.step", encoding="utf-8").read()
n = len(re.findall(r"(?m)^#\d+ = ", data))
print("entities:", n)
print("open shells:", data.count("OPEN_SHELL"))
print("faces:", data.count("FACE_SURFACE"))
