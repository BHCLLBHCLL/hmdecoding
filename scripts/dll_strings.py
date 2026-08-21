import re, sys
path = sys.argv[1]
data = open(path, "rb").read()
print("size:", len(data))
# extract ascii strings
strings = {}
for m in re.finditer(rb"[ -~]{6,}", data):
    s = m.group().decode("ascii", "replace")
    if re.search(r"[A-Za-z]{3}", s):
        strings.setdefault(s, 0)
        strings[s] += 1
pats = re.compile(r"(?i)(gzip|zlib|deflate|zip|compress|magic|header|0x7e|\\x7e|hmbin|binary|.hm|rdata|version|format|section|record|block)", re.I)
hits = sorted([s for s in strings if pats.search(s)], key=lambda s: (-len(s), s))
for s in hits[:150]:
    print(f"{strings[s]:4d}x  {s[:110]}")
