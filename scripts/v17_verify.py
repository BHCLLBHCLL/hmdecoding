"""v17 验证: 解码 vs oracle 全量 ID 比对 (节点/单元), 输出差异明细."""
import sys, time
sys.path.insert(0, "hmdecoder")
from decoder import decode

FILES = {
    "dummy": (r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm",
              "output/ground_truth/v17gt_dummy_nodeids.txt",
              "output/ground_truth/v17gt_dummy_elemids.txt"),
    "seat": (r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\seat_deformer.hm",
             "output/ground_truth/v17gt_seat_nodeids.txt",
             "output/ground_truth/v17gt_seat_elemids.txt"),
}

def gt_ids(path):
    f = open(path)
    f.readline(); cnt = int(f.readline().split()[1])
    ids = set(int(l) for l in f if l.strip())
    f.close()
    return cnt, ids

only = sys.argv[1:] or list(FILES)
for tag in only:
    path, gtn, gte = FILES[tag]
    t0 = time.time()
    m = decode(path)
    nc, gtn = gt_ids(gtn)
    ec, gte = gt_ids(gte)
    dn, de = set(m.nodes), set(m.elements)
    print(f"== {tag}: nodes {len(dn)}/{nc} miss={sorted(gtn-dn)[:10]}{'...' if len(gtn-dn)>10 else ''} "
          f"extra={len(dn-gtn)} | elems {len(de)}/{ec} miss={len(gte-de)} extra={len(de-gte)} "
          f"first_miss={sorted(gte-de)[:10]} | t={time.time()-t0:.1f}s")
    # 差异明细写盘
    with open(f"output/ground_truth/v17_verify_{tag}.txt", "w") as f:
        f.write(f"nodes {len(dn)}/{nc} missing {len(gtn-dn)} extra {len(dn-gtn)}\n")
        f.write("node_missing: " + " ".join(map(str, sorted(gtn-dn))) + "\n")
        f.write(f"elems {len(de)}/{ec} missing {len(gte-de)} extra {len(de-gte)}\n")
        f.write("elem_missing: " + " ".join(map(str, sorted(gte-de))) + "\n")
