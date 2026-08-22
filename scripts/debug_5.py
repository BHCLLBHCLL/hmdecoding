
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64

# WS seg @935609 dump
p = load_payload("WS_3.2_3d_tetra_finish.hm")
sh = 935609
print("== WS seg@935609 header:", [u32(p, sh+j*4) for j in range(8)])
s = sh + 24
for k in range(0, 40, 4):
    print(f"  +{k:3d}: {p[s+k:s+k+4].hex()} u32={u32(p,s+k):>8d} u16=({u16(p,s+k):>5d},{u16(p,s+k+2):>5d})")

# molding1 base=142 vs 182 id sequences
p2 = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\molding1.hm")
for base in (142, 182):
    ids = [u32(p2, base + k*92 + 8) for k in range(8)]
    print(f"molding1 base={base}: ids={ids}")

# body_side _parse_a_type via direct import
from hmdecoder.decoder import _parse_a_type, find_node_section, parse_nodes, row_map_from_nodes, find_elem_segments
p3 = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\body_side.hm")
ns3 = find_node_section(p3)
nodes3, base3 = parse_nodes(p3, ns3)
rm3 = row_map_from_nodes(p3, ns3, base3)
segs3 = find_elem_segments(p3)
print("\nbody_side ns:", ns3)
for sh, segid, cfg71, cnt, X, Y in segs3[:2]:
    got = _parse_a_type(p3, sh, cnt, ns3[1], rm3, max_rec=20)
    print(f"  seg{segid}: {'OK' if got else 'FAIL'} {len(got) if got else 0}")
    if not got:
        # trace
        for s in range(sh+16, sh+64):
            if u32(p3, s) == 0x70241FF5:
                print(f"    CONST@{s-sh}")
