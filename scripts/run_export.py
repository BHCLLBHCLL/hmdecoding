import sys, os
sys.path.insert(0, ".")
from hmdecoder import decode
from hmdecoder.export import export_inp
os.makedirs("output/real_inp", exist_ok=True)
for src, out in (("WS_3.2_3d_tetra_finish.hm", "output/real_inp/ws_tetra.inp"),
                 ("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "output/real_inp/1d_elements.inp")):
    m = decode(src)
    export_inp(m, out, title=f"Source: {src}")
    print(f"{out}: {len(m.nodes)} nodes, {len(m.elements)} elements -> {os.path.getsize(out)} bytes")
