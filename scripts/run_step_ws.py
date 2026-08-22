import sys, os, time
sys.path.insert(0, ".")
from hmdecoder import decode
from hmdecoder.export_step import export_step
t0 = time.time()
m = decode("WS_3.2_3d_tetra_finish.hm")
print("decode:", round(time.time() - t0, 1), "s; nodes:", len(m.nodes), "elems:", len(m.elements), flush=True)
n = export_step(m, "output/real_inp/ws_tetra.step", title="WS_3.2_3d_tetra_finish")
print("ws_tetra.step entities:", n, "size:", os.path.getsize("output/real_inp/ws_tetra.step"), flush=True)
