
import sys, time
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")
log = open("output/ground_truth/v17_struct_timing.txt", "w")
def T(msg, t0):
    log.write(f"{msg}: {time.time()-t0:.1f}s\n"); log.flush()
t0 = time.time()
# replicate struct scan for 68B only
limit = min(len(p), 600_000)
cand_bases = []
pat = b"\x00\x00\x00\x00\x01\x00\x00\x00"
start = 0
while True:
    i = p.find(pat, start, limit)
    if i < 0: break
    base = i - 4
    if base >= 0:
        nid = u32(p, base)
        if 1 <= nid <= 10_000_000:
            cand_bases.append(base)
    start = i + 1
T(f"coarse: {len(cand_bases)} cands", t0)
t1 = time.time()
best = None
seen = set()
checked = 0
for cb in cand_bases:
    for base in range(max(0, cb-64), min(cb+68, limit-20*68), 4):
        if base in seen: continue
        seen.add(base)
        checked += 1
        if checked % 200000 == 0:
            T(f"checked {checked}", t1)
        pre = 0
        for k in range(3):
            rec = base + k*68
            if 1 <= u32(p, rec) <= 10_000_000 and u32(p, rec+4) == 0 and 1 <= u32(p, rec+8) <= 16:
                pre += 1
        if pre < 3: continue
        ok = 0
        ids = set()
        for k in range(30):
            rec = base + k*68
            nid = u32(p, rec)
            if 1 <= nid <= 10_000_000 and abs(d64(p, rec+12)) < 1e9 and u32(p, rec+4) == 0 and 1 <= u32(p, rec+8) <= 16:
                ok += 1; ids.add(nid)
            else:
                break
        if ok >= 25 and len(ids) >= 15:
            cnt = ok
            while base + cnt*68 + 68 <= len(p):
                rec = base + cnt*68
                nid = u32(p, rec)
                if 1 <= nid <= 10_000_000 and abs(d64(p, rec+12)) < 1e9 and u32(p, rec+4) == 0 and 1 <= u32(p, rec+8) <= 16:
                    cnt += 1
                else:
                    break
            log.write(f"candidate: base={base} cnt={cnt}\n"); log.flush()
            if best is None or cnt > best[0]:
                best = (cnt, base)
T("fine done", t1)
log.write(f"best: {best}\n")
log.close()
