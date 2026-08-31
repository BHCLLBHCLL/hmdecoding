
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_elem_segments

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\abaqus\crash_tubes.hm")
segs = find_elem_segments(p)
sh = segs[0][0]
# crash seg1: first record @ sh+24+8 (X u16 @ s+8?), 34B records
# find the slot pattern [X][n1][0][n2]... - locate seg1 area
s = sh + 24
print("seg1 @", sh, "header:", [u32(p, sh+j*4) for j in range(6)])
# scan seg1 records via _parse_b_slots [0][0][X][n1][0][n2] pattern
# count records and find last
pat = b"\x00\x00\x00\x00"
# dump around last slots: iterate A-type? crash_tubes uses u16 slots
# find index of 2280 records: extract slot starts
from decoder import _parse_b_slots
ns = __import__('hmdecoder.decoder', fromlist=['find_node_section']).find_node_section(p)
import struct
rm = {k+1: u32(p, ns[2] + k*ns[3] + ns[4]) for k in range(ns[1])}
got = _parse_b_slots(p, sh, 2280, len(rm), rm, 1)
print("slots seg1 got:", len(got) if got else 0)
# dump the last record region: record 2279 (last)
# find last slot record
if got:
    # find slot start positions
    pass
# dump bytes at sh+24 + 2279*record_len
for rec_len in (34, 38, 30):
    pos = sh + 24 + 2279*rec_len
    print(f"rec_len {rec_len} -> pos {pos}: {p[pos:pos+rec_len].hex()}")
