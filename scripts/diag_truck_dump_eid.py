"""truck: dump 包含 eid 212715 的段结构."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_elem_segments, is_const

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
segs = find_elem_segments(p)

# 找 eid 212715 所在段
target = 212715
pat = target.to_bytes(4, "little")
pos = p.find(pat)
print("eid pos:", pos)

for sh, segid, cfg71, cnt, X, Y in segs:
    if sh <= pos <= sh + 2000:
        print(f"\n段 segid={segid} Y={Y} cfg71={cfg71} cnt={cnt} X={X} sh={sh}")
        print(f"头部 u32: {[u32(p, sh + 4*i) for i in range(8)]}")
        # dump 该段前 6 条记录 (找 CONST 锚)
        anchor = None
        for s in range(sh + 16, sh + 200):
            if is_const(u32(p, s)):
                anchor = s; break
        print("anchor:", anchor, "delta from sh:", anchor - sh if anchor else None)
        if anchor:
            rec = anchor
            for k in range(min(cnt, 6)):
                words = [u32(p, rec + 4*i) for i in range(16)]
                print(f"  rec{k} @{rec}: {words}")
                nxt = p.find(b"\xf5\x1f", rec + 24, min(rec + 200, len(p) - 2))
                while nxt >= 0:
                    if is_const(u32(p, nxt)): break
                    nxt = p.find(b"\xf5\x1f", nxt + 1, min(rec + 200, len(p) - 2))
                if nxt < 0: break
                rec = nxt
        break
