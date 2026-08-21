#!/usr/bin/env python3
"""Parse the hmbatch harvest log into per-file ground-truth JSON."""
import json, re
from pathlib import Path

LOG = Path("output/ground_truth/harvest.log")
OUT = Path("output/ground_truth/corpus_gt.json")
RE = {
    "count": re.compile(r"^count (\S+): (\d+)$"),
    "comp": re.compile(r"^comp id=(\d+) name=(.*)$"),
    "mat": re.compile(r"^mat id=(\d+) name=(.*)$"),
    "prop": re.compile(r"^prop id=(\d+) name=(.*)$"),
    "elem": re.compile(r"^elem id=(\d+) config=(\d+)$"),
}

def parse(log_path: Path):
    files = {}
    cur = None
    for raw in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if line.startswith("==FILE== "):
            cur = {"path": line[len("==FILE== "):].strip(), "counts": {}, "comps": [], "mats": [], "props": [], "config_hist": {}, "config_sampled": 0, "elements_total": None}
            files[cur["path"]] = cur
            continue
        if cur is None:
            continue
        if line.startswith("readfile: "):
            cur["readfile"] = line[len("readfile: "):]
        elif line.startswith("elements_total: "):
            cur["elements_total"] = int(line.split()[1])
        elif line.startswith("config_sampled: "):
            cur["config_sampled"] = int(line.split()[1])
        else:
            for key, rx in RE.items():
                m = rx.match(line)
                if m:
                    if key == "count":
                        cur["counts"][m.group(1)] = int(m.group(2))
                    elif key in ("comp", "mat", "prop"):
                        cur[key + "s"].append({"id": int(m.group(1)), "name": m.group(2)})
                    else:
                        cfg = m.group(2)
                        cur["config_hist"][cfg] = cur["config_hist"].get(cfg, 0) + 1
                    break
    return files

if __name__ == "__main__":
    out = parse(LOG)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=True), encoding="utf-8")
    print("parsed files:", len(out))
    names = [p.split("\\")[-1] for p in out]
    for n in names[:5]:
        d = out[next(k for k in out if k.endswith(n))]
        print(" ", n, d["counts"], "comps:", [c["name"] for c in d["comps"]][:4])
