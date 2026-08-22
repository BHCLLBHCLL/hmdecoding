import sys, os
sys.path.insert(0, ".")
from hmdecoder import decode
from hmdecoder.export_step import export_step
m = decode("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm")
n = export_step(m, "output/real_inp/1d_elements.step", title="1d_elements")
print("1d_elements.step entities:", n, "size:", os.path.getsize("output/real_inp/1d_elements.step"))
