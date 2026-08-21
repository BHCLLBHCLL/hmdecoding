import glob
for pat in ["C:/Program Files/Altair/2019/hm/scripts/**/mpi_split_tets.tcl",
            "C:/Program Files/Altair/2019/hm/scripts/**/dynakey_macromenu.tcl",
            "C:/Program Files/Altair/2019/hm/scripts/**/elementalsystem.tcl"]:
    for f in glob.glob(pat, recursive=True):
        lines = open(f, encoding="utf-8", errors="replace").read().splitlines()
        for i, ln in enumerate(lines):
            if "createelement" in ln:
                lo = max(0, i - 6); hi = min(len(lines), i + 3)
                print("=" * 30, f.split("\\")[-1])
                for j in range(lo, hi):
                    print(f"{j:5d} {lines[j][:110]}")
