import glob, os
# find the fem files and check which are paired with 1d_elements
for f in glob.glob("C:/Program Files/Altair/2019/tutorials/hm/**/*.fem", recursive=True) + glob.glob("C:/Program Files/Altair/2019/tutorials/hm/**/*.key", recursive=True):
    print(os.path.getsize(f), f)
