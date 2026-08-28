"""v17 解码结果全量落盘: nodes/elements dict -> pickle, 供离线差分分析."""
import sys, time, pickle
sys.path.insert(0, "hmdecoder")
from decoder import decode

PATH = sys.argv[1] if len(sys.argv) > 1 else \
    r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm"
TAG = PATH.split("\\")[-1].replace(".hm", "")
t0 = time.time()
m = decode(PATH)
with open(f"output/ground_truth/v17_dec_{TAG}.pkl", "wb") as f:
    pickle.dump({"nodes": m.nodes, "elements": m.elements}, f)
print(f"{TAG}: nodes={len(m.nodes)} elems={len(m.elements)} t={time.time()-t0:.1f}s -> v17_dec_{TAG}.pkl")
