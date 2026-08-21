import glob, os, struct
files = sorted(glob.glob("C:/Program Files/Altair/2019/tutorials/hm/**/*.hm", recursive=True))
files += sorted(glob.glob("C:/Program Files/Altair/2019/tutorials/hm/**/*.hm10", recursive=True))
print("total:", len(files))
cat = {"ascii": [], "gzip_bin": [], "other_bin": []}
for f in files:
    try:
        head = open(f, "rb").read(64)
    except Exception as e:
        print("ERR", f, e); continue
    if head.startswith(b"\x1f\x8b"):
        cat["gzip_bin"].append(f)
    elif head[:4].startswith(b"$$") or head[:4].startswith(b"$HM") or all(c in b" \t\r\n" or 32 <= c < 127 for c in head):
        cat["ascii"].append(f)
    else:
        cat["other_bin"].append(f)
for k, v in cat.items():
    print(f"=== {k}: {len(v)}")
    for f in v:
        sz = os.path.getsize(f)
        print(f"  {sz:>10}  {os.path.basename(f)}")
