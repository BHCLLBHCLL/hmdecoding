# M3.3 验收门禁: 解码侧 Model Browser 文件夹 vs HM oracle (hmbatch 探针输出) 逐文件夹对照
# oracle 由 scripts/m33_folder_oracle.py 采集: output/m33_oracle/<file>.oracle.txt
# 路由规则与 hm_gui._collector_folders 保持一致 (Sets/Load/Assemblies 名称启发式).
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from hmdecoder.decoder import decode

PAIRS = [
    ("frame_assembly_1", r"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/frame_assembly_1.hm"),
    ("frame_assembly_3", r"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/frame_assembly_3.hm"),
    ("truck", r"C:/Program Files/Altair/2019/tutorials/hm/truck.hm"),
]
REPORT = os.path.join(os.path.dirname(__file__), "..", "output", "m33_gate_report.txt")

# 解码侧路由 -> oracle 实体类型
FOLDER_ROUTES = [
    ("Components", "components", "comps"),
    ("Materials", "mats", "mats"),
    ("Properties", "props", "props"),
    ("Groups", "groups", "groups"),
    ("Sets", "sets", "sets:"),
    ("Load", "loadcols", "loads:"),
    ("Assemblies", "assemblies", "asm:"),
]

def parse_oracle(path):
    d, cur = {}, None
    for line in open(path, encoding="utf-8", errors="ignore"):
        m = re.match(r"^== (\w+) (\d+) ==", line)
        if m:
            cur = m.group(1)
            d[cur] = []
            continue
        m = re.match(r"^(\w+) (\d+) ?(.*)$", line)
        if m and cur and m.group(1) == cur:
            d[cur].append((int(m.group(2)), m.group(3).strip()))
    return d

def ours_folder(kind, model):
    if kind == "comps":
        return sorted(model.comps.items())
    if kind == "mats":
        return sorted(model.mats.items())
    if kind == "props":
        return sorted(model.props.items())
    if kind == "groups":
        return sorted(model.groups.items())
    out = []
    for cid, nm in model.others:
        if kind == "sets:" and nm.startswith(("Set_", "SLAVE_", "C_S^_")):
            out.append((cid, nm))
        elif kind == "loads:" and nm.startswith("Airbag"):
            out.append((cid, nm))
        elif kind == "asm:" and nm.startswith("assem"):
            out.append((cid, nm))
    return sorted(out)

def main():
    lines = []
    for tag, fp in PAIRS:
        orf = os.path.join(os.path.dirname(__file__), "..", "output",
                           "m33_oracle", os.path.basename(fp) + ".oracle.txt")
        o = parse_oracle(orf)
        m = decode(fp)
        lines.append(f"\n===== {tag} (db {m.db_version:.2f}) =====")
        for label, otype, kind in FOLDER_ROUTES:
            orc = o.get(otype, [])
            oid = {i for i, _ in orc}
            ours = ours_folder(kind, m)
            ok = {i for i, _ in ours}
            miss = sorted(oid - ok)
            extra = sorted(ok - oid)
            # 名称对照 (oracle 有名称时)
            nmiss = []
            onames = {i: nm for i, nm in orc if nm}
            for i, nm in ours:
                if i in onames and onames[i] != nm:
                    nmiss.append((i, onames[i], nm))
            verdict = "OK" if not miss and not extra and not nmiss else "DIFF"
            lines.append(
                f"{label:12} oracle={len(orc):4} ours={len(ours):4} [{verdict}]"
                + (f"  miss={miss[:6]}{'…' if len(miss) > 6 else ''}" if miss else "")
                + (f"  extra={extra[:6]}{'…' if len(extra) > 6 else ''}" if extra else "")
                + (f"  name-diff={nmiss[:4]}" if nmiss else ""))
        # 未解码家族 (oracle 有, 解码无对应文件夹)
        gaps = []
        for t in ("blocks", "connectors", "titles", "tags"):
            if o.get(t):
                gaps.append(f"{t}={len(o[t])}")
        if gaps:
            lines.append(f"{'(未解码)':12} oracle 实体存在但无解码: {' '.join(gaps)}")
    # Others 残影说明
    lines.append("\n说明: type516 XtraNodes*/RigidWallPlan* 为 sets 族记录, 其中部分 id "
                 "在 HM 中已不存在 (删除残留), 统一留 Others 不计入 Sets.")
    text = "\n".join(lines)
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write(text)
    print(text)

if __name__ == "__main__":
    main()
