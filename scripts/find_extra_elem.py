import sys, gzip, struct
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
m = D.decode("WS_3.2_3d_tetra_finish.hm")
eids = sorted(m.elements)
print("count:", len(eids), "range:", eids[0], eids[-1])
# expected eid set: 291462..324028 with 31843 members — find suspicious eids (gaps + extra)
# check for elements with < 3 nodes
for eid in eids:
    e = m.elements[eid]
    if len(e.nodes) < 3:
        print("suspicious elem", eid, "nodes:", e.nodes, "config:", e.config)
# check duplicate positions: parse again and see if any eid appears twice at different offsets
recs = {}
for i in range(0, len(p) - 30):
    if D.u32(p, i + 4) == 0 and D.u32(p, i + 8) == 0:
        eid = D.u32(p, i)
        flag = D.u16(p, i + 12)
        if eid < 100000 or flag not in (359, 460):
            continue
        refs = [D.u16(p, i + 14), D.u16(p, i + 18), D.u16(p, i + 22), D.u16(p, i + 26)]
        if not all(r <= 6408 for r in refs):
            continue
        recs.setdefault(eid, []).append((i, flag, refs))
dups = {e: v for e, v in recs.items() if len(v) > 1}
print("duplicate eids:", len(dups))
for e, v in list(dups.items())[:5]:
    print("  ", e, v)
