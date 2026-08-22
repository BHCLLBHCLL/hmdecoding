
import sys, os, struct
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, d64

zfiles = ["2_holes.hm", "Full_Motion_TV_Mount_Partly_Open.hm", "Realizations.hm", "Insert_planes.hm",
          "TETMESH_PM.hm", "arm_bracket.hm", "base_bracket.hm", "bm_housing.hm", "bracket.hm",
          "c-channel0.hm", "channel.hm", "chordal_dev.hm", "clip_defeature.hm", "clip_midsurface.hm",
          "clip_repair.hm", "electrical_housing.hm", "hyperbeam.hm", "plate_hole.hm",
          "dummy_positioner.hm", "seat_deformer.hm", "chapter2_2.hm"]
for fname in zfiles:
    path = f"C:/Program Files/Altair/2019/tutorials/hm/{fname}"
    if not os.path.exists(path):
        path = f"C:/Program Files/Altair/2019/tutorials/hm/interfaces/ansys/{fname}"
    if not os.path.exists(path):
        path = f"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/{fname}"
    if not os.path.exists(path):
        print(f"{fname}: MISSING"); continue
    p = load_payload(path)
    print(f"{fname}: db={d64(p,4)} len={len(p)}")
