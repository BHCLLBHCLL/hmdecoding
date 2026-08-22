import sys, os
sys.path.insert(0, ".")
from hmdecoder import decode
from hmdecoder.decoder import GeoPoint
from hmdecoder.export_iges import export_iges
m1 = decode("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm")
m1.geo_points = {1: GeoPoint(1, 5.0, -5.0, 0.0), 2: GeoPoint(2, 5.0, 5.0, 0.0),
                 3: GeoPoint(3, -5.0, 5.0, 0.0), 4: GeoPoint(4, -5.0, -5.0, 0.0)}
m1._variant_a_lines = [(18, 1, 2), (19, 2, 3), (20, 3, 4), (21, 4, 1), (36, 1, 2), (37, 2, 3), (38, 3, 4), (39, 4, 1)]
np_, nl_ = export_iges(m1, "output/real_inp/1d_elements_geom.iges")
print("1d:", np_, "pts", nl_, "lines", os.path.getsize("output/real_inp/1d_elements_geom.iges"), "B")
m2 = decode("WS_3.2_3d_tetra_finish.hm")
np2, nl2 = export_iges(m2, "output/real_inp/ws_geom.iges")
print("ws:", np2, "pts", nl2, "lines", os.path.getsize("output/real_inp/ws_geom.iges"), "B")
# 自检 T 行
for path in ("output/real_inp/1d_elements_geom.iges", "output/real_inp/ws_geom.iges"):
    lines = open(path).read().splitlines()
    print(path, "tail:", lines[-1].strip()[:60], "| lines:", len(lines))
